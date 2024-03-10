import numpy as np
import scipy.signal as sig
import matplotlib.pyplot as plt
import multiprocessing as mp


class Filter(mp.Process):
    def __init__(self, destinations: tuple, b_coefficients, a_coefficients, samplerate=44100, type='ba',
                 remove_offset=True, normalize=True, queue_size=4):
        super().__init__()
        self.destinations = destinations
        self.in_queue = mp.Queue(queue_size)
        self.out_queue = mp.Queue(queue_size)
        self.b = b_coefficients
        self.a = a_coefficients
        self.samplerate = samplerate
        self.type = type
        self.remove_offset = remove_offset
        self.normazlize = normalize

    def run(self):
        while True:
            data = self.in_queue.get()
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

            for destination in self.destinations:
                destination.put(data)

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
        ax2.plot(freq_hz, np.rad2deg(angles), 'g')
        ax2.set_ylabel('Angle (degrees)', color='g')
        ax2.grid()
        ax2.axis('tight')
        plt.show()


class ButterFilter(Filter):
    def __init__(self, destinations: tuple, N: int, cutoff: int, samplerate=44100, type='ba', remove_offset=True,
                 normalize=True, queue_size=4):
        b, a = sig.butter(N=N, Wn=(cutoff * 2 * np.pi), fs=samplerate, btype='lowpass')
        super().__init__(self, destinations, b, a, samplerate, type, remove_offset, normalize, queue_size)


class FIRWINFilter(Filter):
    def __init__(self, destinations: tuple, N: int, cutoff: int, samplerate=44100, type='ba', remove_offset=True,
                 normalize=True, queue_size=4):
        b = sig.firwin(N, cutoff, fs=samplerate)
        Filter.__init__(self, destinations, b, 1, samplerate, type, remove_offset, normalize, queue_size)


class HanningWindow(mp.Process):
    def __init__(self, destinations: tuple, queue_size=4):
        super().__init__()
        self.destinations = destinations
        self.in_queue = mp.Queue(queue_size)
        self.out_queue = mp.Queue(queue_size)

    def run(self):
        while True:
            data = self.in_queue.get()
            data *= np.hanning(len(data))[:, np.newaxis]

            for destination in self.destinations:
                destination.put(data)
