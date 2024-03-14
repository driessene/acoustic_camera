import sounddevice as sd
import cupy as np
from time import sleep
from Management import pipeline


def print_audio_devices():
    """
    Print all available audio devices
    """
    print("Microphone Devices:")
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            print(f"Device {i}: {device['name']}, Channels: {device['max_input_channels']}")


class AudioRecorder(pipeline.Stage):
    """
    Records audio and pushes it into destionatnations.

    Args:
        device_id (str): Device id to record the audio. Use print_audio_devices for help finding available audio devices
        samplerate (int): Sampling rate of the device
        blocksize (int): Number of samples per block of audio
        destinations (tuple): Tuple of destinations to push audio to
    """
    def __init__(self, device_id, samplerate=44100, channels=8, blocksize=1024, destinations=None):
        """
        Initializes the device recorder
        :param device_id: Device id to record the audio. Use print_audio_devices for help finding available audio devices
        :param samplerate: Sampling rate of the device
        :param channels: Number of samples per block of audio
        :param blocksize: Number of samples per block of audio
        :param destinations: Tuple of destinations to push audio to
        """
        super().__init__(0, 0, destinations)
        self.device_id = device_id
        self.samplerate = samplerate
        self.channels = channels
        self.blocksize = blocksize
        self.stream = None

    def _audio_callback(self, indata, frames, time, status):
        """
        Continously called by sounddevice. Records audio and pushes it into destinations
        """
        if status:
            print(status)
        self.destination_queue_put(indata)

    def start(self):
        """
        Starts the audio stream
        :return: None
        """
        self.stream = sd.InputStream(
            device=self.device_id,
            channels=self.channels,
            samplerate=self.samplerate,
            blocksize=self.blocksize,
            callback=self._audio_callback
        )
        self.stream.start()

    def stop(self):
        """
        Stops the audio stream
        :return: None
        """
        if self.stream:
            self.stream.stop()
            self.stream.close()



class AudioSimulator(pipeline.Stage):
    """
    Audio simulator. Produces audio similar to AudioRecorder
    """
    def __init__(self,
                 frequencies: tuple,
                 doas: tuple,
                 spacing: float = 0.25,  # In meters. Causes spacing to scale with frequency like in real life
                 snr: float = 50,
                 samplerate: int = 44100,
                 channels: int = 6,
                 blocksize: int = 1024,
                 speed_of_sound: float = 343.0,
                 sleep: bool = True,
                 destinations=None
                 ):
        """
        Initialize the simulator
        :param frequencies: A tuple of signals to produce. The tuple hold the frequency of each signal
        :param doas: A tuple of coresponding directions-of-arrivals for the signals in "frequencies"
        :param spacing: The spacing between each element in meters
        :param snr: The signal-to-noise ratio of the elements
        :param samplerate: The sampling rate of the simulator
        :param channels:
        :param blocksize: Number of samples per block of audio
        :param speed_of_sound: Speed of sound
        :param sleep: If true, sleep to simulate the delay between audio samples like real life
        :param destinations: A list of destinations to push simulated audio to
        """
        super().__init__(0, 0, destinations)
        self.frequencies = frequencies
        self.doas = doas
        self.spacing = spacing
        self.snr = snr
        self.samplerate = samplerate
        self.channels = channels
        self.blocksize = blocksize
        self.speed_of_sound = speed_of_sound
        self.sleep = sleep

        # Mock inherited properties
        self.virtual_channels = self.channels

        # pre-compute
        self.time_vector = None
        self.signals = None
        self.array_factor = None
        self.signal_matrix = np.zeros((self.blocksize, self.channels), dtype=np.complex128)
        self.signal_power = None
        self.noise_power = None
        self.update_precompute()


    def update_precompute(self):
        """
        Call whenever any properties change
        :return: None
        """
        # Time
        self.time_vector = np.arange(self.blocksize) / self.samplerate

        # Signal
        signals = [np.exp(2j * np.pi * freq * self.time_vector) for freq in self.frequencies]
        array_factors = [np.exp(-2j * np.pi * (self.spacing / (self.speed_of_sound / freq)) * np.arange(self.channels) * np.sin(np.deg2rad(doa))) for (doa, freq) in zip(self.doas, self.frequencies)]
        self.signal_matrix = np.sum(np.array([np.outer(sig, af) for sig, af in zip(signals, array_factors)]), axis=0)
        self.signal_matrix /= np.max(np.abs(self.signal_matrix))
        self.signal_power = np.mean(np.abs(self.signal_matrix) ** 2)

        # Noise
        self.noise_power = 10 ** ((10 * np.log10(self.signal_power) - self.snr) / 20)

    def run(self):
        """
        The process. Runs forever, generating audio blocks and pushes to destinations
        :return: None
        """
        while True:
            # Generate noise
            noise = np.random.normal(0, np.sqrt(self.noise_power), (self.blocksize, self.channels)) \
                    + 1j * np.random.normal(0, np.sqrt(self.noise_power), (self.blocksize, self.channels))
            signal = self.signal_matrix + noise
            signal /= np.max(np.abs(signal))

            if self.sleep:
                sleep(self.blocksize / self.samplerate)  # simulate delay for recording

            self.destination_queue_put(signal)
