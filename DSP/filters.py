import numpy as np
import scipy.signal as sig


class Filter:
    def __init__(self, b_coefficients, a_coefficients, remove_offset=True, normalize=True):
        self.b = b_coefficients
        self.a = a_coefficients
        self.remove_offset = remove_offset
        self.normazlize = normalize

    def process(self, data):
        if self.remove_offset:
            data -= np.mean(data, axis=0, keepdims=True)
        if self.normazlize:
            data /= np.max(np.abs(data), axis=0, keepdims=True)
        return sig.lfilter(self.b, self.a, data, axis=0)

class ButterLowpassFilter(Filter):
    def __init__(self, N:int, Wn:int, samplerate=44100, remove_offset=True, normalize=True):
        b, a = sig.butter(N=2, Wn=(Wn * 2 * np.pi), fs=samplerate, btype='lowpass')
        Filter.__init__(self, b, a, remove_offset, normalize)
