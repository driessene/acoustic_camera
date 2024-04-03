from DSP.Sinks import plotters
from DSP.Processes import direction_of_arrival, filters
from DSP.Sources import simulators
from pyqtgraph.Qt import QtWidgets
import numpy as np


def main():

    # Variables
    samplerate = 44100
    blocksize = 44100
    spacing = 0.5
    snr = 50
    channels = 8
    sleep = False

    # Sources
    sources = [simulators.Source(675, 10), simulators.Source(775, 30)]

    # Recorder to get data
    recorder = simulators.AudioSimulator(
        sources=sources,
        spacing=spacing,
        snr=snr,
        samplerate=samplerate,
        num_channels=channels,
        blocksize=blocksize,
        sleep=sleep
    )

    # Filter
    filt = filters.FIRWINFilter(
        N=101,
        num_channels=channels,
        cutoff=1000,
        samplerate=samplerate,
        method='filtfilt',
    )

    # MUSIC
    music = direction_of_arrival.MUSIC(num_channels=channels, num_sources=4, spacing=spacing)

    # Plotter
    app = QtWidgets.QApplication([])
    plot = plotters.SingleLinePlotter(
        title='MUSIC',
        x_label='Angle',
        y_label='Power',
        blocksize=1000,
        x_data=np.linspace(-90, 90, 1000),
        x_range=(-90, 90),
        y_range=(0, 1)
    )

    # Linking
    recorder.link_to_destination(filt, 0)
    filt.link_to_destination(music, 0)
    music.link_to_destination(plot, 0)

    # Start processes
    recorder.start()
    filt.start()
    music.start()
    plot.show()
    app.exec()


if __name__ == '__main__':
    main()
