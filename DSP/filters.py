import numpy as np
import scipy.signal as sig
import matplotlib.pyplot as plt
from Management import pipeline


class Filter(pipeline.Stage):
    """
    Filters 2D data using FIR or IIR digital filters. Applied filters along the 0 axis.
    """
    def __init__(self,
                 b_coefficients,
                 a_coefficients,
                 samplerate,
                 num_channels,
                 method='filtfilt',
                 remove_offset=True,
                 normalize=True,
                 queue_size=4,
                 destinations=None):
        """
        Initialized the filter
        :param b_coefficients: B coefficients of the digital filter
        :param a_coefficients: A coefficients of the digital filter
        :param samplerate: Samerate of the input data
        :param num_channels: The number of channels in the signal matrix
        :param method:
            lfilter: A typical digital filter
            filtfilt: Applied a digital filter forwards, the backwards. Has no phase change but squares the response
                of the digital filter.
        :param remove_offset: Removes the 0 Hz offset from the input data if true
        :param normalize: Sets the max value of the data to 1 if true
        :param queue_size: The size of the input queue
        :param destinations: Where to push the filtered data. Object should inherit Stage
        """
        super().__init__(1, queue_size, destinations)
        self.b = b_coefficients
        self.a = a_coefficients
        self.samplerate = samplerate
        self.num_channels = num_channels
        self.method = method
        self.remove_offset = remove_offset
        self.normazlize = normalize
        self.filter_order = max(self.b.size, self.a.size) - 1
        self.initial_conditions = np.zeros((self.filter_order, self.num_channels))

    def run(self):
        """
        Runs the filter along input data. Ran by a process
        :return: None
        """
        while True:
            data = self.input_queue_get()[0]

            if self.remove_offset:
                data -= np.mean(data, axis=0, keepdims=True)
            if self.normazlize:
                data /= np.max(np.abs(data), axis=0, keepdims=True)
            if self.method == 'lfilter':
                data, self.initial_conditions = sig.lfilter(self.b, self.a, data, axis=0, zi=self.initial_conditions)
            elif self.method == 'filtfilt':
                data = sig.filtfilt(self.b, self.a, data, axis=0)
            else:
                raise NotImplementedError
            self.destination_queue_put(data)

    def plot_response(self):
        """
        Plots the response of the filter using matplotlib. Blocking
        :return: None
        """
        w, h = sig.freqz(self.b, self.a)
        freq_hz = w * self.samplerate / (2 * np.pi)  # Convert frequency axis to Hz
        fig, ax1 = plt.subplots()
        ax1.set_title('Digital filter frequency response')
        ax1.plot(freq_hz, (20 * np.log10(abs(h))), 'b')
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
    """
    Implements a butterworth filter
    """
    def __init__(self, N: int, cutoff: int, samplerate, num_channels, method='filtfilt', remove_offset=True,
                 normalize=True, queue_size=4, destinations = None):
        """
        Initializes a butterworth filter
        :param N: Order of the filter
        :param cutoff: Cutoff frequency of the filter in Hz
        :param samplerate: See Filter
        :param method: See Filter
        :param remove_offset: See Filter
        :param normalize: See Filter
        :param queue_size: See Filter
        :param destinations: See Filter
        """
        b, a = sig.butter(N=N, Wn=(cutoff * 2 * np.pi), fs=samplerate, btype='lowpass')
        super().__init__(b, a, samplerate, num_channels, method, remove_offset, normalize, queue_size, destinations)


class FIRWINFilter(Filter):
    """
    Implements a filter using an ideal FIR filter via the window method. Very sharp cutoff, ideal in digital systems
    """
    def __init__(self, N: int, cutoff: int, samplerate, num_channels, method='filtfilt', remove_offset=True,
                 normalize=True, queue_size=4, destinations=None):
        """
        Initializes a FIRWINFilter
        :param N: Length of the FIR filter
        :param cutoff: Cutoff frequency of the filter in Hz
        :param samplerate: See Filter
        :param method: See Filter
        :param remove_offset: See Filter
        :param normalize: See Filter
        :param queue_size: See Filter
        :param destinations: See Filter
        """
        b = sig.firwin(N, cutoff, fs=samplerate)
        super().__init__(b, np.array(1), samplerate, num_channels, method, remove_offset, normalize, queue_size, destinations)


class HanningWindow(pipeline.Stage):
    """
    Applied a hanning window to input data
    """
    def __init__(self, queue_size=4, destinations=None):
        """
        Initializes a HanningWindow
        :param queue_size: The size of the input queue
        :param destinations: Where to push the filtered data. Object should inherit Stage
        """
        super().__init__(1, queue_size, destinations)

    def run(self):
        """
        Runs the window along input data. Ran by a process
        :return: None
        """
        while True:
            data = self.input_queue_get()[0]
            data *= np.hanning(len(data))[:, np.newaxis]
            self.destination_queue_put(data)
