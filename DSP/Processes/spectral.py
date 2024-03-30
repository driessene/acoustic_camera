import numpy as np
from Management import pipeline
import scipy.fft as fft


class FFT(pipeline.Stage):
    """
    Computes magnitude and phase of FFT for input data.
    """
    def __init__(self, queue_size=4, destinations=None):
        """
        Initializes the Periodogram
        :param queue_size: The size of the input queue
        :param destinations: Where to push
        """
        super().__init__(1, queue_size, destinations)

    def run(self):
        """
        Continuously applies FFT to each channel of the input data
        :return: None
        """
        while True:
            self.destination_queue_put(fft.fft(self.input_queue_get()[0], axis=0))
