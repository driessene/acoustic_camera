import numpy as np
from Management import pipeline
import scipy.fft as fft


class FFT(pipeline.Stage):
    """
    Applies an FFT to data
    """
    def __init__(self, port_size=4, destinations=None):
        super().__init__(1, port_size, destinations)

    def run(self):
        self.port_put(fft.fft(self.port_get()[0], axis=0))
