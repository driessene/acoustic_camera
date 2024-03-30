import numpy as np
from Management import pipeline
import scipy.fft as fft


class FFT(pipeline.Stage):
    """
    Computes magnitude and phase of FFT for input data.
    """
    def __init__(self, return_pwr_ph=True, num_workers=-1, queue_size=4, destinations=None):
        """
        Initializes the Periodogram
        :param return_pwr_ph: If True, push (amp, ang). If false, push complex fft. Default is true
        :param num_workers: The number of workers to compute fft. If program hangs, lower this value
        :param queue_size: The size of the input queue
        :param destinations: Where to push (f, pxx)
        """
        super().__init__(1, queue_size, destinations)
        self.return_pwr_ph = return_pwr_ph
        self.num_workers = num_workers

    def run(self):
        """
        Continuously applies FFT to each channel of the input data. Pushes (amplitude, phase) to destinations
        :return:
        """
        while True:
            data = self.input_queue_get()[0]
            f = fft.fftshift(fft.fft(data, axis=0, workers=self.num_workers))
            if self.return_pwr_ph:
                self.destination_queue_put((np.abs(f) ** 2, np.angle(f)))
            else:
                self.destination_queue_put(f)
