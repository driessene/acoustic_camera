import numpy as np
import scipy.signal as sig
import matplotlib.pyplot as plt


class BAFilter:
    def __init__(self, b_coefficients, a_coefficients, samplerate=44100, remove_offset=True, normalize=True):
        self.b = b_coefficients
        self.a = a_coefficients
        self.samplerate = samplerate
        self.remove_offset = remove_offset
        self.normazlize = normalize

    def process(self, data):
        if self.remove_offset:
            data -= np.mean(data, axis=0, keepdims=True)
        if self.normazlize:
            data /= np.max(np.abs(data), axis=0, keepdims=True)
        return sig.lfilter(self.b, self.a, data, axis=0)

    def plot_response(self):
        w, h = sig.freqz(self.b, self.a)
        freq_hz = w * self.samplerate / (2 * np.pi)  # Convert frequency axis to Hz
        fig, ax1 = plt.subplots()
        ax1.set_title('Digital filter frequency response')
        ax1.plot(freq_hz, 20 * np.log10(abs(h)), 'b')
        ax1.set_ylabel('Amplitude [dB]', color='b')
        ax1.set_xlabel('Frequency [Hz]')
        ax2 = ax1.twinx()
        angles = np.unwrap(np.angle(h))
        ax2.plot(freq_hz, angles, 'g')
        ax2.set_ylabel('Angle (radians)', color='g')
        ax2.grid()
        ax2.axis('tight')
        plt.show()


class ButterFilter(BAFilter):
    def __init__(self, N:int, cutoff:int, samplerate=44100, remove_offset=True, normalize=True):
        b, a = sig.butter(N=N, Wn=(cutoff * 2 * np.pi), fs=samplerate, btype='lowpass')
        BAFilter.__init__(self, b, a, samplerate=samplerate, remove_offset=remove_offset, normalize=normalize)


class FIRWINFilter(BAFilter):
    def __init__(self, N:int, cutoff:int, samplerate=44100, remove_offset=True, normalize=True):
        b = sig.firwin(N, cutoff, fs=samplerate)
        BAFilter.__init__(self, b, 1, samplerate=samplerate, remove_offset=remove_offset, normalize=normalize)


class HanningFilter:
    @staticmethod
    def process(data):
        return data * np.hanning(len(data))[:, np.newaxis]
