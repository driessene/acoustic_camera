from Management import pipeline
import numpy as np
from time import sleep


class Source:
    """
    Mathematical representation of an audio source in a space
    """

    def __init__(self, frequency, theta):
        """
        Initializes a source
        :param frequency: The frequency in Hz of the audio source
        :param theta: The direction of arrival of the source to a source recorder
        """
        self.frequency = frequency
        self.theta = theta


class AudioSimulator(pipeline.Stage):
    """
    Simulates audio recordings. Can be used in place of AudioRecorder for testing
    """
    def __init__(self,
                 sources: list[Source],
                 spacing: float = 0.25,  # In meters. Causes spacing to scale with frequency like in real life
                 snr: float = 50,
                 samplerate: int = 44100,
                 num_channels: int = 6,
                 blocksize: int = 1024,
                 speed_of_sound: float = 343.0,
                 sleep: bool = True,
                 destinations=None
                 ):
        """
        :param sources: The sources to simulate
        :param spacing: Spacing, in meters, of the microphone array
        :param snr: Signal to noise ratio of the simulation
        :param samplerate: The samplerate of the simulation
        :param num_channels: The number of channles of the simulation
        :param blocksize: The number of samples per block
        :param speed_of_sound: The speed of sound of the environment
        :param sleep: If true, sleep between simulations.
            This represents the acutal time it takes to get data for a recorder
        :param destinations: Where to push simulation data. Object should inherit from Stage
        """
        super().__init__(0, 0, destinations)
        self.sources = sources
        self.spacing = spacing
        self.snr = snr
        self.samplerate = samplerate
        self.channels = num_channels
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
        Updates properties that do not need to be updated every frame. Call whenever a property is changed
        :return: None
        """
        # Time
        self.time_vector = np.arange(self.blocksize) / self.samplerate

        # Source
        frequencies = [source.frequency for source in self.sources]
        doas = [source.theta for source in self.sources]

        # Generate Signals
        signals = [np.exp(2j * np.pi * freq * self.time_vector) for freq in frequencies]

        # Generate steering vectors corresponding to signals
        steering_vectors = [np.exp(-2j * np.pi * self.spacing * np.arange(self.channels)
                                   * np.sin(np.deg2rad(doa))) for (doa, freq) in zip(doas, frequencies)]

        # Calculate each channel using signals and steering vectors. Real values only such as in real-life
        self.signal_matrix = np.sum(np.array([np.outer(sig, af) for sig, af in zip(signals, steering_vectors)]),
                                    axis=0).real

        # Powers
        self.signal_power = np.mean(np.abs(self.signal_matrix) ** 2)
        self.noise_power = 10 ** ((10 * np.log10(self.signal_power) - self.snr) / 20)

    def run(self):
        """
        Updated properties that need to be updated every frame (ie. noise). Pushed data to desintations. Called by a
        process.
        :return: None
        """
        # Generate noise and normalize
        noise = np.random.normal(0, np.sqrt(self.noise_power), (self.blocksize, self.channels))
        signal = self.signal_matrix + noise
        signal /= np.max(np.abs(signal))

        if self.sleep:
            sleep(self.blocksize / self.samplerate)  # simulate delay for recording

        self.port_put(signal)
