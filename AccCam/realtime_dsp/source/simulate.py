import AccCam.direction_of_arrival as doa
import AccCam.realtime_dsp.pipeline as pipe
from time import sleep


class AudioSimulator(pipe.Stage):
    """
    Simulates audio recordings. Can be used in place of AudioRecorder for testing
    """
    def __init__(self,
                 structure: doa.Structure,
                 wavevectors: list[doa.WaveVector],
                 wait: bool = True,
                 randomize_phase: bool = True,
                 destinations=None
                 ):
        """
        :param structure: The structure which to get the simulation from.
        :param wavevectors: The wavevectors to simulate for.
        :param wait: If true, sleep between simulations. This represents the real time it takes to get data for a
            recorder.
        :param destinations: Where to push simulation data. Object should inherit from Stage
        """
        super().__init__(0, 0, destinations)
        self.structure = structure
        self.wavevectors = wavevectors
        self.wait = wait
        self.randomize_phase = randomize_phase

        # Mock inherited properties
        self.channels = len(self.structure.elements)
        self.virtual_channels = self.channels

    def run(self):
        """
        Updated properties that need to be updated every frame (i.e. noise)
        :return: None
        """
        # Generate noise and normalize
        signal = self.structure.simulate_audio(self.wavevectors, random_phase=self.randomize_phase)

        if self.wait:
            sleep(self.structure.blocksize / self.structure.samplerate)  # simulate delay for recording

        self.port_put(pipe.Message(signal))
