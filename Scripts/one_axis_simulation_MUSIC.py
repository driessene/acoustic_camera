from DSP import source_simulators, filters, direction_of_arrival, plotters
from pyqtgraph.Qt import QtWidgets


def main():

    # Variables
    samplerate = 44100
    blocksize = 44100
    spacing = 0.254
    snr = 50
    channels = 8
    sleep = False

    # Sources
    sources = [source_simulators.Source(675, 10), source_simulators.Source(700, 30)]

    # Recorder to get data
    recorder = source_simulators.AudioSimulator(
        sources=sources,
        spacing=spacing,
        snr=snr,
        samplerate=samplerate,
        channels=channels,
        blocksize=blocksize,
        sleep=sleep
    )

    # Filter
    filt = filters.FIRWINFilter(
        N=101,
        num_channels=channels,
        cutoff=1000,
        samplerate=44100,
        method='filtfilt',
    )

    # MUSIC
    music = direction_of_arrival.MUSIC(num_channels=channels, num_sources=2, spacing=0.5)

    # Plotter
    app = QtWidgets.QApplication([])
    plot = plotters.SingleLinePlotter(
        title='Spectral',
        x_label='Hz',
        y_label='Power',
        x_range=(0, 1000),
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
