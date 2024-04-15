from .__config__ import *
import scipy.fft as fft


class FFT(Stage):
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
        self.port_put(Message(f))
