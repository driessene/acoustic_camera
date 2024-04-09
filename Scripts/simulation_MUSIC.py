from DSP.Sinks import plotters_ptqtgraph
from DSP.Processes import direction_of_arrival, filters
from DSP.Sources import simulators
from Geometry.arbitrary import Element, WaveVector, SteeringMatrix
from pyqtgraph.Qt import QtWidgets
import numpy as np


def main():

    # Variables
    samplerate = 44100
    blocksize = 1024
    wave_number = 1.46
    speed_of_sound = 343
    snr = 50

    # Sources
    elements = [
        Element([0.00, 0, 0]),
        Element([0.25, 0, 0]),
        Element([0.50, 0, 0]),
        Element([0.75, 0, 0]),
        Element([1.00, 0, 0]),
        Element([1.25, 0, 0]),
        Element([1.50, 0, 0]),
        Element([1.75, 0, 0])
    ]

    wave_vectors = [
        WaveVector([wave_number * 1.0, 0, np.deg2rad(10)], speed_of_sound),
        WaveVector([wave_number * 1.2, 0, np.deg2rad(50)], speed_of_sound)
    ]

    # Recorder to get data
    recorder = simulators.AudioSimulator(
        elements=elements,
        wave_vectors=wave_vectors,
        snr=snr,
        samplerate=samplerate,
        num_channels=len(elements),
        blocksize=blocksize,
        sleep=True
    )

    # Filter
    filt = filters.FIRWINFilter(
        N=101,
        num_channels=len(elements),
        cutoff=1000,
        samplerate=samplerate,
        method='filtfilt',
    )

    # MUSIC
    test_angles = np.linspace(-np.pi / 2, np.pi / 2, 1000)
    matrix = SteeringMatrix(
        elements=elements,
        azimuths=np.array([0]),
        inclinations=test_angles,
        wavenumber=wave_number,
        wave_speed=speed_of_sound
    )
    music = direction_of_arrival.MUSIC(
        steering_matrix=matrix,
        num_sources=4
    )

    # Plotter
    app = QtWidgets.QApplication([])
    plot = plotters_pyqtplot.SingleLinePlotter(
        title='MUSIC',
        x_label='Inclination',
        y_label='Power',
        blocksize=blocksize,
        x_data=np.rad2deg(test_angles),
        x_range=(-90, 90),
        y_range=(0, 1)
    )

    # Linking
    recorder.link_to_destination(filt, 0)
    filt.link_to_destination(music, 0)
    music.link_to_destination(plot, 0)

    # Start processes
    recorder.start()
    filt.start()
    music.start()
    plot.show()
    app.exec()


if __name__ == '__main__':
    main()
