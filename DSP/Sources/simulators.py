from Management import pipeline
import numpy as np
from time import sleep
from functools import cached_property


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

    @cached_property
    def time_vector(self):
        return np.arange(self.blocksize) / self.samplerate

    @cached_property
    def signals(self):
        frequencies = [source.frequency for source in self.sources]
        return [np.exp(2j * np.pi * freq * self.time_vector) for freq in frequencies]

    @cached_property
    def steering_vectors(self):
        frequencies = [source.frequency for source in self.sources]
        doas = [source.theta for source in self.sources]
        return [np.exp(-2j * np.pi * self.spacing * np.arange(self.channels)
                                   * np.sin(np.deg2rad(doa))) for (doa, freq) in zip(doas, frequencies)]

    @cached_property
    def signal_matrix(self):
        return np.sum(np.array([np.outer(sig, af) for sig, af in zip(self.signals, self.steering_vectors)]),
                                    axis=0).real

    @cached_property
    def signal_power(self):
        return np.mean(np.abs(self.signal_matrix) ** 2)

    @cached_property
    def noise_power(self):
        return 10 ** ((10 * np.log10(self.signal_power) - self.snr) / 20)

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
