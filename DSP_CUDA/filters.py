import cupy as np
import cupyx.scipy.signal as sig
import matplotlib.pyplot as plt
from Management import pipeline


class Filter(pipeline.Stage):
    """
    Filters audio signals
    """
    def __init__(self,
                 b_coefficients,
                 a_coefficients,
                 samplerate=44100,
                 type='filtfilt',
                 remove_offset=True,
                 normalize=True,
                 queue_size=4,
                 destinations=None):
        """
        Initializes the filter
        :param b_coefficients: B coeficients of the filter
        :param a_coefficients: A coeficients of the filter
        :param samplerate: Samplerate of the recording
        :param type: either 'filtfilt' or 'ba'
            = ba: A normal discrete BA filter
            - filtfilt: a forwards-backwards filting. Squares the responce of the filter, but has no phase change
        :param remove_offset: If True, removes the DC component of the signal
        :param normalize: If True, normalizes the signal by making the max value 1
        :param queue_size: How many blocks of data to hold in the input queue
        :param destinations: Tuple of destinations to push filtered signals to
        """
        super().__init__(1, queue_size, destinations)
        self.b = b_coefficients
        self.a = a_coefficients
        self.samplerate = samplerate
        self.type = type
        self.remove_offset = remove_offset
        self.normazlize = normalize

    def run(self):
        """
        The process. Runs forever, filtering any data in the input queue and pushes filtered data to destinations
        :return: None
        """
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
        """
        Plots the filter response
        :return: None
        """
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

    def plot_coefficients(self):
        """
        Plots the filter coefficients
        :return: None
        """
        fig, ax1 = plt.subplots()
        if not isinstance(self.b, (float, int)):
            ax1.set_title('Digital filter frequency response')
            ax1.plot(np.arange(self.b.shape[0]).get(), self.b.get())
            ax1.set_ylabel('B Amplitude', color='b')
            ax1.set_xlabel('N')
        if not isinstance(self.a, (float, int)):
            ax2 = ax1.twinx()
            ax2.plot(np.arange(self.a.shape[0]).get(), self.b.get())
            ax2.set_ylabel('A Amplitude', color='g')
            ax2.grid()
            ax2.axis('tight')
        plt.show()


class ButterFilter(Filter):
    """
    A butterworth filter
    """
    def __init__(self, N: int, cutoff: int, samplerate=44100, type='filtfilt', remove_offset=True,
                 normalize=True, queue_size=4, destinations = None):
        """
        Initializes a butterworth filter
        :param N: Order of the filter
        :param cutoff: The cutoff frequency
        :param samplerate: See "Filter" description
        :param type: See "Filter" description
        :param remove_offset: See "Filter" description
        :param normalize: See "Filter" description
        :param queue_size: See "Filter" description
        :param destinations: See "Filter" description
        """
        b, a = sig.butter(N=N, Wn=(cutoff * 2 * np.pi), fs=samplerate, btype='lowpass')
        super().__init__(b, a, samplerate, type, remove_offset, normalize, queue_size, destinations)



class FIRWINFilter(Filter):
    """
    An ideal filter implemented using the windowing method. Capable of very sharp cutoffs
    """
    def __init__(self, N: int, cutoff: int, samplerate=44100, type='filtfilt', remove_offset=True,
                 normalize=True, queue_size=4, destinations=None):
        """
        Initializes the FIRWINFilter
        :param N: Length of the fir filter
        :param cutoff: The cutoff frequency
        :param samplerate: See "Filter" description
        :param type: See "Filter" description
        :param remove_offset: See "Filter" description
        :param normalize: See "Filter" description
        :param queue_size: See "Filter" description
        :param destinations: See "Filter" description
        """
        b = sig.firwin(N, cutoff, fs=samplerate)
        super().__init__(b, 1, samplerate, type, remove_offset, normalize, queue_size, destinations)

class HanningWindow(pipeline.Stage):
    """
    Applies a hanning window to data
    """
    def __init__(self, queue_size=4, destinations=None):
        """
        Initializes the HanningWindow
        :param queue_size: How many blocks of data to hold in the input queue
        :param destinations: Tuple of destinations to push filtered signals to
        """
        super().__init__(1, queue_size, destinations)

    def run(self):
        """
        The process. Runs forever, windowing any data in the input queue and pushes filtered data to destinations
        :return: None
        """
        while True:
            data = self.input_queue_get()[0]
            data *= np.hanning(len(data))[:, np.newaxis]
            self.destination_queue_put(data)
