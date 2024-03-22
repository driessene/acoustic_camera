import numpy as np
from Management import pipeline
import scipy.signal as sig

class Periodogram(pipeline.Stage):
    def __init__(self, samplerate=44100, queue_size=4, destinations=None):
        super().__init__(1, queue_size, destinations)
        self.samplerate = samplerate

    def run(self):
        while True:
            data = self.input_queue_get()[0]
            f = np.zeros_like(data)
            pxx = np.zeros_like(data)
            for i, channel in enumerate(data.T):
                f[:, i], pxx[:, i] = sig.periodogram(channel, fs=self.samplerate)
            self.destination_queue_put((f, pxx))
