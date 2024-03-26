from DSP.Sinks import plotters
from DSP.Processes import spectral, filters
from DSP.Sources import simulators
from pyqtgraph.Qt import QtWidgets


def main():

    # Variables
    samplerate = 44100
    blocksize = 4096
    spacing = 0.254
    snr = 50
    channels = 8
    sleep = False

    # Sources
    sources = [simulators.Source(675, 10), simulators.Source(700, 30)]

    # Recorder to get data
    recorder = simulators.AudioSimulator(
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

    # Sprectal
    spec = spectral.Periodogram(samplerate)

    # Plotter
    app = QtWidgets.QApplication([])
    plot = plotters.MultiLinePlotterParametric(
        title='Spectral',
        x_label='Hz',
        y_label='Power',
        x_range=(0, 1000),
        y_range=(0, 0.1),
        num_lines=channels,
        blocksize=blocksize//2+1
    )

    # Linking
    recorder.link_to_destination(filt, 0)
    filt.link_to_destination(spec, 0)
    spec.link_to_destination(plot, 0)

    # Start processes
    recorder.start()
    filt.start()
    spec.start()
    plot.show()
    app.exec()


if __name__ == '__main__':
    main()
