from DSP.Sinks import plotters
from DSP.Processes import spectral, filters
from DSP.Sources import simulators
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
        samplerate=samplerate,
        method='filtfilt',
    )

    # Sprectal
    fft = spectral.FFT()

    # Plotter
    app = QtWidgets.QApplication([])
    plot = plotters.FFTApplication(samplerate, blocksize, channels, freq_range=(600, 800))

    # Linking
    recorder.link_to_destination(filt, 0)
    filt.link_to_destination(fft, 0)
    fft.link_to_destination(plot, 0)

    # Start processes
    recorder.start()
    filt.start()
    fft.start()
    plot.show()
    app.exec()


if __name__ == '__main__':
    main()
