from DSP import source_simulators, filters, direction_of_arrival, plotters
from pyqtgraph.Qt import QtWidgets


def main():

    # Variables
    samplerate = 44100
    blocksize = 10000
    spacing = 0.5
    snr = 20
    sleep = False

    # Sources
    sources_x = [
        source_simulators.Source(600, 10),
        source_simulators.Source(800, 50)
    ]
    sources_y = [
        source_simulators.Source(600, 20),
        source_simulators.Source(800, 60)
    ]
    sources_z = [
        source_simulators.Source(600, 40),
        source_simulators.Source(800, 80)
    ]

    # Recorder to get data
    recorder_x = source_simulators.AudioSimulator(
        sources=sources_x,
        spacing=spacing,
        snr=snr,
        samplerate=samplerate,
        channels=8,
        blocksize=blocksize,
        sleep=sleep
    )
    recorder_y = source_simulators.AudioSimulator(
        sources=sources_y,
        spacing=spacing,
        snr=snr,
        samplerate=samplerate,
        channels=8,
        blocksize=blocksize,
        sleep=sleep
    )
    recorder_z = source_simulators.AudioSimulator(
        sources=sources_z,
        spacing=spacing,
        snr=snr,
        samplerate=samplerate,
        channels=8,
        blocksize=blocksize,
        sleep=sleep
    )

    # FIR window filter to remove noise
    fir_x = filters.FIRWINFilter(N=100, cutoff=2000, samplerate=samplerate, num_channels=8, method='filtfilt')
    fir_y = filters.FIRWINFilter(N=100, cutoff=2000, samplerate=samplerate, num_channels=8, method='filtfilt')
    fir_z = filters.FIRWINFilter(N=100, cutoff=2000, samplerate=samplerate, num_channels=8, method='filtfilt')

    # MUSIC Algorithm
    music_x = direction_of_arrival.MUSIC(spacing=0.5, num_channels=8, num_sources=2)
    music_y = direction_of_arrival.MUSIC(spacing=0.5, num_channels=8, num_sources=2)
    music_z = direction_of_arrival.MUSIC(spacing=0.5, num_channels=8, num_sources=2)

    # Application plotter
    app = QtWidgets.QApplication([])
    plotter = plotters.ThreeAxisApplication(
        blocksize=blocksize,
        num_music_angles=1000,
        x_num_channels=8,
        y_num_channels=8,
        z_num_channels=8,
    )

    # Linking

    # Recorders to FIR
    recorder_x.link_to_destination(fir_x, 0)
    recorder_y.link_to_destination(fir_y, 0)
    recorder_z.link_to_destination(fir_z, 0)

    # FIR to MUSIC
    fir_x.link_to_destination(music_x, 0)
    fir_y.link_to_destination(music_y, 0)
    fir_z.link_to_destination(music_z, 0)

    # Everything to plotter
    music_x.link_to_destination(plotter, 0)
    music_y.link_to_destination(plotter, 1)
    music_z.link_to_destination(plotter, 2)
    fir_x.link_to_destination(plotter, 3)
    fir_y.link_to_destination(plotter, 4)
    fir_z.link_to_destination(plotter, 5)
    recorder_x.link_to_destination(plotter, 6)
    recorder_y.link_to_destination(plotter, 7)
    recorder_z.link_to_destination(plotter, 8)

    # Start processes
    recorder_x.start()
    recorder_y.start()
    recorder_z.start()
    fir_x.start()
    fir_y.start()
    fir_z.start()
    music_x.start()
    music_y.start()
    music_z.start()
    plotter.show()
    app.exec()


if __name__ == '__main__':
    main()
