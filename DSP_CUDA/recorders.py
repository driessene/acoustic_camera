import sounddevice as sd
import cupy as np
from time import sleep
import multiprocessing as mp


def print_audio_devices():
    print("Microphone Devices:")
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            print(f"Device {i}: {device['name']}, Channels: {device['max_input_channels']}")


class AudioRecorder:
    def __init__(self, destinations: tuple, device_id, samplerate=44100, channels=8, blocksize=1024):
        self.destinations = destinations
        self.device_id = device_id
        self.samplerate = samplerate
        self.channels = channels
        self.blocksize = blocksize
        self.stream = None

    def _audio_callback(self, indata, frames, time, status):
        if status:
            print(status)
        for destination in self.destinations:
            destination.put(indata)

    def start(self):
        self.stream = sd.InputStream(
            device=self.device_id,
            channels=self.channels,
            samplerate=self.samplerate,
            blocksize=self.blocksize,
            callback=self._audio_callback
        )
        self.stream.start()

    def stop(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()


class AudioSimulator(mp.Process):
    def __init__(self,
                 destinations: tuple,
                 frequencies: tuple,
                 doas: tuple,
                 spacing: float = 0.25,  # In meters. Causes spacing to scale with frequency like in real life
                 snr: float = 50,
                 samplerate: int = 44100,
                 channels: int = 6,
                 blocksize: int = 1024,
                 speed_of_sound: float = 343.0,
                 sleep: bool = True
                 ):

        super().__init__()
        self.destinations = destinations
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

    # Call whenever a system property changes
    def update_precompute(self):
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
        while True:
            # Generate noise
            noise = np.random.normal(0, np.sqrt(self.noise_power), (self.blocksize, self.channels)) \
                    + 1j * np.random.normal(0, np.sqrt(self.noise_power), (self.blocksize, self.channels))
            signal = self.signal_matrix + noise

            if self.sleep:
                sleep(self.blocksize / self.samplerate)  # simulate delay for recording

            for destination in self.destinations:
                destination.put(signal)
