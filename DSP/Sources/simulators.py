from .. import config

if config.USE_CUPY:
    import cupy as np
else:
    import numpy as np

from Management import pipeline
from Geometry.geometry import Element, SteeringVector, WaveVector
from time import sleep
from functools import cached_property


class AudioSimulator(pipeline.Stage):
    """
    Simulates audio recordings. Can be used in place of AudioRecorder for testing
    """
    def __init__(self,
                 wave_vectors: list,
                 elements: list,
                 snr: float = 50,
                 samplerate: int = 44100,
                 blocksize: int = 1024,
                 speed_of_sound: float = 343.0,
                 sleep: bool = True,
                 destinations=None
                 ):
        """
        :param wave_vectors: The wave vectors to simulate
        :param elements: The elements to simulate
        :param snr: Signal to noise ratio of the simulation
        :param samplerate: The samplerate of the simulation
        :param blocksize: The number of samples per block
        :param sleep: If true, sleep between simulations.
            This represents the acutal time it takes to get data for a recorder
        :param destinations: Where to push simulation data. Object should inherit from Stage
        """
        super().__init__(0, 0, destinations)
        self.wave_vectors = wave_vectors
        self.elements = elements
        self.snr = snr
        self.samplerate = samplerate
        self.blocksize = blocksize
        self.sleep = sleep

        # Mock inherited properties
        self.channels = len(self.elements)
        self.virtual_channels = self.channels

    @cached_property
    def time_vector(self):
        return np.arange(self.blocksize) / self.samplerate

    @cached_property
    def waveforms(self):
        frequencies = [wave_vector.frequency for wave_vector in self.wave_vectors]
        return [np.exp(2j * np.pi * freq * self.time_vector) for freq in frequencies]

    @cached_property
    def steering_vectors(self):
        return [SteeringVector(self.elements, wave_vector) for wave_vector in self.wave_vectors]

    @cached_property
    def signal_matrix(self):
        return np.sum(np.array([np.outer(sig, steering.vector) for sig, steering in zip(self.waveforms, self.steering_vectors)]),
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

        self.port_put(pipeline.Message(signal))
