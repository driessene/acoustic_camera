from DSP import source_recorders, filters, direction_of_arrival, plotters
from pyqtgraph.Qt import QtWidgets


def main():

    # Variables
    samplerate = 44100
    blocksize = 1000

    # Recorder to get data
    recorder = source_recorders.AudioRecorder(
        device_id=14,
        samplerate=samplerate,
        channels=8,
        blocksize=blocksize,
        channel_map=[2, 3, 4, 5, 6, 7]
    )

    # FIR Filter
    fir_filter = filters.FIRWINFilter(10, 2000, samplerate=samplerate, num_channels=8)

    # Window

    # MUSIC Algorithm
    music = direction_of_arrival.MUSIC(spacing=0.5, num_channels=6, num_sources=2)

    # Application plotter
    app = QtWidgets.QApplication([])
    # plotter = plotters.MultiLinePlotter(
    #     title='MUSIC',
    #     x_label='Angle (deg)',
    #     y_label='MUSIC',
    #     x_range=(-90, 90),
    #     y_range=(-1, 1),
    #     num_lines=channels,
    #     blocksize=blocksize
    # )
    plotter = plotters.SingleLinePlotter(
        title='MUSIC',
        x_label='Angle (deg)',
        y_label='MUSIC',
        x_range=(-90, 90),
        y_range=(0, 1)
    )

    # Linking
    recorder.link_to_destination(fir_filter, 0)
    fir_filter.link_to_destination(music, 0)
    music.link_to_destination(plotter, 0)

    # Start processes
    recorder.start()
    fir_filter.start()
    music.start()
    plotter.show()
    app.exec()


if __name__ == '__main__':
    main()
