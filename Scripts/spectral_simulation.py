from DSP.Sinks import applications, plotters
from DSP.Processes import filters, spectral
from DSP.Sources import simulators
from Geometry.arbitrary import Element, WaveVector
from pyqtgraph.Qt import QtWidgets
import numpy as np


def main():

    # Variables
    samplerate = 44100
    blocksize = 44100
    wave_number = 3.94  # 10 inches
    speed_of_sound = 343
    snr = 50
    sleep = False

    # Sources
    elements = [
        Element([0, 0, 0]),
        Element([0.5, 0, 0]),
        Element([1, 0, 0]),
        Element([1.5, 0, 0]),
        Element([2, 0, 0]),
        Element([2.5, 0, 0]),
        Element([3, 0, 0]),
        Element([3.5, 0, 0])
    ]
    wave_vectors = [
        WaveVector([wave_number, 0, 0.175], speed_of_sound),   # 10 deg
        WaveVector([wave_number, 0, 0.873], speed_of_sound)    # 50 deg
    ]

    # Recorder to get data
    recorder = simulators.AudioSimulator(
        elements=elements,
        wave_vectors=wave_vectors,
        snr=snr,
        samplerate=samplerate,
        num_channels=len(elements),
        blocksize=blocksize,
        sleep=sleep
    )

    # Filter
    filt = filters.FIRWINFilter(
        N=101,
        num_channels=len(elements),
        cutoff=1000,
        samplerate=samplerate,
        method='filtfilt',
    )

    # Sprectal
    fft = spectral.FFT()

    # Plotter
    app = QtWidgets.QApplication([])
    plot = plotters.SingleLinePlotter(
        title='FFT',
        x_label='K',
        y_label='FFT',
        blocksize=1000,
        x_range=(-90, 90),
        y_range=(0, 1)
    )

    # Linking
    recorder.link_to_destination(filt, 0)
    filt.link_to_destination(fft, 0)
    fft.link_to_destination(plot, 0)

    # Start processes
    recorder.start()
    filt.start()
    fft.start()
    plot.show()


if __name__ == '__main__':
    main()
