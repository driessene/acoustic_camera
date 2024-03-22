import numpy as np
from Management import pipeline
import scipy.signal as sig

class Periodogram(pipeline.Stage):
    """
    Estimates power spectral density for each channel using a periodogram. Pushes a tuple of (f, pxx)
    """
    def __init__(self, samplerate=44100, queue_size=4, destinations=None):
        """
        Initializes the Periodogram
        :param samplerate: The samplerate of the source
        :param queue_size: The size of the input queue
        :param destinations: Where to push (f, pxx)
        """
        super().__init__(1, queue_size, destinations)
        self.samplerate = samplerate

    def run(self):
        """
        Continuously applies periodogram to each channel of the input data. Pushes (f, pxx) to destinations
        :return:
        """
        while True:
            data = self.input_queue_get()[0]
            f = np.zeros_like(data)
            pxx = np.zeros_like(data)
            for i, channel in enumerate(data.T):
                f[:, i], pxx[:, i] = sig.periodogram(channel, fs=self.samplerate)
            self.destination_queue_put((f, pxx))
