import numpy as np
import AccCam.realtime_dsp.pipeline as pipe


class FFT(pipe.Stage):
    """
    Applies an FFT to data
    """
    def __init__(self, return_abs=False, port_size=4, destinations=None):
        self.return_abs = return_abs
        super().__init__(1, port_size, destinations)

    def run(self):
        message = self.port_get()[0]
        data = message.payload

        f = np.fft.fft(data, axis=0)
        if self.return_abs:
            f = np.abs(f)
        self.port_put(pipe.Message(f))
