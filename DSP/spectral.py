import numpy as np
import scipy.fft as fft
from Pipeline import Stage, Message


class FFT(Stage):
    """
    Applies an FFT to data
    """
    def __init__(self, return_abs=False, port_size=4, destinations=None):
        self.return_abs = return_abs
        super().__init__(1, port_size, destinations)

    def run(self):
        f = fft.fft(self.port_get()[0].payload, axis=0)
        if self.return_abs:
            f = np.abs(f)
        self.port_put(Message(f))
