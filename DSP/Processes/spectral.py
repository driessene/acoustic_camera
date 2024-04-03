import numpy as np
from Management import pipeline
import scipy.fft as fft


class FFT(pipeline.Stage):
    """
    Computes magnitude and phase of FFT for input data.
    """
    def __init__(self, port_size=4, destinations=None):
        """
        Initializes the Periodogram
        :param port_size: The size of the input queue
        :param destinations: Where to push
        """
        super().__init__(1, port_size, destinations)

    def run(self):
        """
        Applies FFT to each channel of the input data
        :return: None
        """
        self.port_put(fft.fft(self.port_get()[0], axis=0))
