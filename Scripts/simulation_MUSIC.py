from DSP_CUDA import recorders, filters, direction_of_arrival, plotters
from pyqtgraph.Qt import QtWidgets


def main():

    # Variables
    samplerate = 44100
    blocksize = 1024
    spacing = 0.254
    snr = 50
    channels = 6

    # Start Qt
    app = QtWidgets.QApplication([])

    # Recorder to get data
    recorder_x = recorders.AudioSimulator(
        frequencies=(675, 600),
        doas=(10, 30),
        spacing=spacing,
        snr=snr,
        samplerate=samplerate,
        channels=channels,
        blocksize=blocksize,
        sleep=True
    )
    recorder_y = recorders.AudioSimulator(
        frequencies=(675, 600),
        doas=(20, 50),
        spacing=spacing,
        snr=snr,
        samplerate=samplerate,
        channels=channels,
        blocksize=blocksize,
        sleep=True
    )
    recorder_z = recorders.AudioSimulator(
        frequencies=(675, 600),
        doas=(30, 60),
        spacing=spacing,
        snr=snr,
        samplerate=samplerate,
        channels=channels,
        blocksize=blocksize,
        sleep=True
    )

    # FIR window filter to remove noise
    fir_x = filters.FIRWINFilter(N=100, cutoff=1200, type='filtfilt')
    fir_y = filters.FIRWINFilter(N=100, cutoff=1200, type='filtfilt')
    fir_z = filters.FIRWINFilter(N=100, cutoff=1200, type='filtfilt')

    # Hanning filter to remove spectral leakage
    hanning_x = filters.HanningWindow()
    hanning_y = filters.HanningWindow()
    hanning_z = filters.HanningWindow()

    # MUSIC Algorithm
    music_x = direction_of_arrival.MUSIC(spacing=0.5, num_mics=6, num_sources=2)
    music_y = direction_of_arrival.MUSIC(spacing=0.5, num_mics=6, num_sources=2)
    music_z = direction_of_arrival.MUSIC(spacing=0.5, num_mics=6, num_sources=2)

    # Application plotter
    plotter = plotters.ThreeAxisApplication(
        blocksize=blocksize,
        num_music_angles=1000,
        x_num_channels=6,
        y_num_channels=6,
        z_num_channels=6,
    )

    # Linking

    # Recorders to FIR
    recorder_x.link_to_destination(fir_x, 0)
    recorder_y.link_to_destination(fir_y, 0)
    recorder_z.link_to_destination(fir_z, 0)

    # FIR to hanning
    fir_x.link_to_destination(hanning_x, 0)
    fir_y.link_to_destination(hanning_y, 0)
    fir_z.link_to_destination(hanning_z, 0)

    # Hanning to MUSIC
    hanning_x.link_to_destination(music_x, 0)
    hanning_y.link_to_destination(music_y, 0)
    hanning_z.link_to_destination(music_z, 0)

    # Everything to plotter
    recorder_x.link_to_destination(plotter, 2)
    recorder_y.link_to_destination(plotter, 5)
    recorder_z.link_to_destination(plotter, 8)
    hanning_x.link_to_destination(plotter, 1)
    hanning_y.link_to_destination(plotter, 4)
    hanning_z.link_to_destination(plotter, 7)
    music_x.link_to_destination(plotter, 0)
    music_y.link_to_destination(plotter, 3)
    music_z.link_to_destination(plotter, 6)

    # Start processes
    recorder_x.start()
    recorder_y.start()
    recorder_z.start()
    fir_x.start()
    fir_y.start()
    fir_z.start()
    hanning_x.start()
    hanning_y.start()
    hanning_z.start()
    music_x.start()
    music_y.start()
    music_z.start()
    plotter.show()
    app.exec()


if __name__ == '__main__':
    main()
