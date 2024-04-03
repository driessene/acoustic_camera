from DSP.Sinks import plotters
from DSP.Processes import filters
from DSP.Sources import simulators
from pyqtgraph.Qt import QtWidgets


def main():

    # Variables
    samplerate = 44100
    blocksize = samplerate//10
    spacing = 0.254
    snr = 50
    channels = 8
    sleep = False

    # Sources
    sources = [simulators.Source(500, 10), simulators.Source(800, 30)]

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
        N=501,
        cutoff=1500,
        samplerate=samplerate,
        num_channels=channels,
        method='lfilter',
    )
    filt.plot_response()

    # Plotter
    app = QtWidgets.QApplication([])
    plot = plotters.MultiLinePlotter(
        title='Waveforms',
        x_label='N',
        y_label='A',
        x_range=(0, 200),
        y_range=(-1, 1),
        num_lines=channels,
        blocksize=blocksize
    )

    # Linking
    recorder.link_to_destination(filt, 0)
    filt.link_to_destination(plot, 0)

    # Start processes
    recorder.start()
    filt.start()
    plot.show()
    app.exec()


if __name__ == '__main__':
    main()
