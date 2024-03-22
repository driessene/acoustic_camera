from DSP import source_simulators, filters, spectral, plotters
from pyqtgraph.Qt import QtWidgets


def main():

    # Variables
    samplerate = 44100
    blocksize = 10240
    spacing = 0.254
    snr = 20
    channels = 8
    sleep = False

    # Sources
    sources = [source_simulators.Source(675, 10), source_simulators.Source(1000, 30)]

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
        cutoff=2000,
        samplerate=44100,
        type='filtfilt',
    )

    # Spectral
    spec = spectral.Periodogram(samplerate)

    # Application plotter
    app = QtWidgets.QApplication([])
    plotter = plotters.MultipleLinePlotterParametric(
        title='MUSIC',
        x_label='Angle (deg)',
        y_label='MUSIC',
        x_range=(0, 1000),
        y_range=(0, 0.01),
        num_lines=channels,
        blocksize=blocksize,
    )

    # Linking
    recorder.link_to_destination(filt, 0)
    filt.link_to_destination(spec, 0)
    spec.link_to_destination(plotter, 0)

    # Start processes
    recorder.start()
    filt.start()
    spec.start()
    plotter.show()
    app.exec()


if __name__ == '__main__':
    main()
