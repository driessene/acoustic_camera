from DSP import source_simulators, filters, playback, plotters
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
    sources = [source_simulators.Source(500, 10), source_simulators.Source(800, 30)]

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
        N=501,
        cutoff=1500,
        samplerate=samplerate,
        method='filtfilt',
        num_channels=channels
    )
    filt.plot_response()

    # Playback
    play = playback.AudioPlayback(samplerate, blocksize)

    # Plotter
    app = QtWidgets.QApplication([])
    plot = plotters.MultiLinePlotter(
        title='Waveforms',
        x_label='N',
        y_label='A',
        x_range=(1000, 1500),
        y_range=(-1, 1),
        num_lines=channels,
        blocksize=blocksize
    )

    # Linking
    recorder.link_to_destination(filt, 0)
    filt.link_to_destination(play, 0)
    filt.link_to_destination(plot, 0)

    # Start processes
    recorder.start()
    filt.start()
    play.start()
    plot.show()
    app.exec()


if __name__ == '__main__':
    main()
