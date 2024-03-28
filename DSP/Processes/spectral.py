import numpy as np
from Management import pipeline
import scipy.signal as sig
import scipy.fft as fft


class FFT(pipeline.Stage):
    """
    Computes magnitude and phase of FFT for input data.
    """
    def __init__(self, return_amp_ang=True, queue_size=4, destinations=None):
        """
        Initializes the Periodogram
        :param return_amp_ang: If True, push (amp, ang). If false, push complex fft. Defult is true
        :param queue_size: The size of the input queue
        :param destinations: Where to push (f, pxx)
        """
        super().__init__(1, queue_size, destinations)
        self.return_amp_ang = return_amp_ang

    def run(self):
        """
        Continuously applies FFT to each channel of the input data. Pushes (amplitude, phase) to destinations
        :return:
        """
        while True:
            data = self.input_queue_get()[0]
            f = fft.fft(data, axis=0)
            if self.return_amp_ang:
                self.destination_queue_put((np.abs(f), np.angle(f)))
            else:
                self.destination_queue_put(f)
