from DSP_CUDA import recorders, filters, direction_of_arrival, plotters
from pyqtgraph.Qt import QtWidgets


def main():

    # Variables
    samplerate = 44100
    blocksize = 1024
    frequencies = (675, 600)
    doas = (10, 60)
    spacing = 0.254
    snr = 50
    channels = 6

    # Start Qt
    app = QtWidgets.QApplication([])

    # Recorder to get data
    recorder = recorders.AudioSimulator(
        frequencies=frequencies,
        doas=doas,
        spacing=spacing,
        snr=snr,
        samplerate=samplerate,
        channels=channels,
        blocksize=blocksize,
        sleep=True
    )

    # FIR window filter to remove noise
    fir = filters.FIRWINFilter(N=100, cutoff=1200, type='filtfilt')

    # Hanning filter to remove spectral leakage
    hanning = filters.HanningWindow()

    # MUSIC Algorithm
    music = direction_of_arrival.MUSIC(spacing=0.5, num_mics=6, num_sources=2)

    # Plotter
    plotter = plotters.SingleLinePlotter(
        title='MUSIC Spectrum',
        x_label='Angle (Deg)',
        y_label='Music',
        x_range=(-90, 90),
        y_range=(0, 1)
    )

    # Linking
    recorder.link_to_destination(fir, 0)
    fir.link_to_destination(hanning, 0)
    hanning.link_to_destination(music, 0)
    music.link_to_destination(plotter, 0)

    # Start processes
    recorder.start()
    fir.start()
    hanning.start()
    music.start()
    plotter.show()
    app.exec()


if __name__ == '__main__':
    main()
