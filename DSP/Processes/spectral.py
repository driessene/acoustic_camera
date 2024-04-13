from .. import config

if config.USE_CUPY:
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
        f = fft.fft(self.port_get()[0].payload, axis=0)
        if self.abs:
            f = np.abs(f)
        self.port_put(pipeline.Message(f))
