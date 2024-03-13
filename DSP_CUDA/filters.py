import cupy as np
import cupyx.scipy.signal as sig
import matplotlib.pyplot as plt
from Management import pipeline


class Filter(pipeline.Stage):
    def __init__(self,
                 b_coefficients,
                 a_coefficients,
                 samplerate=44100,
                 type='filtfilt',
                 remove_offset=True,
                 normalize=True,
                 queue_size=4,
                 destinations=None):
        super().__init__(1, queue_size, destinations)
        self.b = b_coefficients
        self.a = a_coefficients
        self.samplerate = samplerate
        self.type = type
        self.remove_offset = remove_offset
        self.normazlize = normalize

    def run(self):
        while True:
            data = self.input_queue_get()[0]
            if self.remove_offset:
                data -= np.mean(data, axis=0, keepdims=True)
            if self.normazlize:
                data /= np.max(np.abs(data), axis=0, keepdims=True)
            if self.type == 'ba':
                data = sig.lfilter(self.b, self.a, data, axis=0)
            elif self.type == 'filtfilt':
                data = sig.filtfilt(self.b, self.a, data, axis=0)
            else:
                raise NotImplementedError

            self.destination_queue_put(data)

    def plot_response(self):
        w, h = sig.freqz(self.b, self.a)
        freq_hz = w * self.samplerate / (2 * np.pi)  # Convert frequency axis to Hz
        fig, ax1 = plt.subplots()
        ax1.set_title('Digital filter frequency response')
        ax1.plot(freq_hz.get(), (20 * np.log10(abs(h))).get(), 'b')
        ax1.set_ylabel('Amplitude [dB]', color='b')
        ax1.set_xlabel('Frequency [Hz]')
        ax2 = ax1.twinx()
        angles = np.unwrap(np.angle(h))
        ax2.plot(freq_hz.get(), np.rad2deg(angles).get(), 'g')
        ax2.set_ylabel('Angle (degrees)', color='g')
        ax2.grid()
        ax2.axis('tight')
        plt.show()


class ButterFilter(Filter):
    def __init__(self, N: int, cutoff: int, samplerate=44100, type='filtfilt', remove_offset=True,
                 normalize=True, queue_size=4, destinations = None):
        b, a = sig.butter(N=N, Wn=(cutoff * 2 * np.pi), fs=samplerate, btype='lowpass')
        super().__init__(b, a, samplerate, type, remove_offset, normalize, queue_size, destinations)


class FIRWINFilter(Filter):
    def __init__(self, N: int, cutoff: int, samplerate=44100, type='filtfilt', remove_offset=True,
                 normalize=True, queue_size=4, destinations=None):
        b = sig.firwin(N, cutoff, fs=samplerate)
        super().__init__(b, 1, samplerate, type, remove_offset, normalize, queue_size, destinations)


class HanningWindow(pipeline.Stage):
    def __init__(self, queue_size=4, destinations=None):
        super().__init__(1, queue_size, destinations)

    def run(self):
        while True:
            data = self.input_queue_get()[0]
            data *= np.hanning(len(data))[:, np.newaxis]
            self.destination_queue_put(data)
