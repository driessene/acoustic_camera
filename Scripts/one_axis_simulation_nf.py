from DSP import recorders, filters, direction_of_arrival, plotters
from pyqtgraph.Qt import QtWidgets


def main():

    # Variables
    samplerate = 44100
    blocksize = 1024
    spacing = 0.254
    snr = 20
    channels = 6
    sleep = False

    # Signals
    signals = [
        recorders.Signal(675, 10),
        recorders.Signal(600, 30)
    ]

    # Recorder to get data
    recorder = recorders.AudioSimulator(
        signals=signals,
        spacing=spacing,
        snr=snr,
        samplerate=samplerate,
        channels=channels,
        blocksize=blocksize,
        sleep=sleep
    )

    # MUSIC Algorithm
    music = direction_of_arrival.MUSIC(spacing=0.5, num_mics=6, num_sources=2)

    # Application plotter
    app = QtWidgets.QApplication([])
    plotter = plotters.SingleLinePlotter(
        title='MUSIC',
        x_label='Angle (deg)',
        y_label='MUSIC',
        x_range=(-90, 90),
        y_range=(0, 1)
    )

    # Linking
    recorder.link_to_destination(music, 0)
    music.link_to_destination(plotter, 0)

    # Start processes
    recorder.start()
    music.start()
    plotter.show()
    app.exec()


if __name__ == '__main__':
    main()
