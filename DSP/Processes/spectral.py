from .. import __use_cupy__

if __use_cupy__:
    import cupy as np
else:
    import numpy as np

from Management import pipeline
import scipy.fft as fft


class FFT(pipeline.Stage):
    """
    Applies an FFT to data
    """
    def __init__(self, abs=False, port_size=4, destinations=None):
        self.abs = abs
        super().__init__(1, port_size, destinations)

    def run(self):
        f = fft.fft(self.port_get()[0], axis=0)
        if self.abs:
            f = np.abs(f)
        self.port_put(f)
