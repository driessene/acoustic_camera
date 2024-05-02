import numpy as np
import AccCam.realtime_dsp.pipeline as pipe


class FFT(pipe.Stage):
    """
    Applies an FFT to data
    """
    def __init__(self, type: str, shift=False, port_size=4, destinations=None):
        """
        :param type: The type of output.
            - complex: return the raw complex output of the fft,
            - phase: return the phase of the fft
            - abs: return the absolute value of the fft
            - power: return the power of the fft
        :param shift: If true, move 0hz to the center of the array. Best for plotting
        """
        self.type = type
        self.shift = shift
        super().__init__(1, port_size, destinations)

    def run(self):
        message = self.port_get()[0]
        data = message.payload

        f = np.fft.fft(data, axis=0)

        if self.shift:
            f = np.fft.fftshift(f)

        match self.type:
            case 'complex':
                pass
            case 'phase':
                f = np.angle(f)
            case 'abs':
                f = np.abs(f)
            case 'power':
                f = np.square(np.abs(f))

        self.port_put(pipe.Message(f))
