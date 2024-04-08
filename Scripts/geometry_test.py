from DSP.Sinks import plotters
from DSP.Processes import direction_of_arrival, filters
from DSP.Sources import simulators
from Geometry.arbitrary import Element, WaveVector, SteeringMatrix
from pyqtgraph.Qt import QtWidgets
from Utilities import array
import numpy as np


def main():

    # Variables
    samplerate = 44100
    blocksize = 44100
    wave_number = 3.94  # 10 inches
    speed_of_sound = 343
    snr = 50
    channels = 8
    delta_theta = np.pi / 1000
    sleep = False

    # Sources
    elements = [
        Element([0, 0, 0]),
        Element([0.5, 0, 0]),
        Element([1, 0, 0]),
        Element([1.5, 0, 0]),
        Element([2, 0, 0]),
        Element([2.5, 0, 0]),
        Element([3, 0, 0]),
        Element([3.5, 0, 0])
    ]
    wave_vectors = [
        WaveVector([wave_number, 0.175, 0], speed_of_sound),   # 10 deg
        WaveVector([wave_number, 0.873, 0], speed_of_sound)    # 50 deg
    ]

    # Recorder to get data
    recorder = simulators.AudioSimulator(
        elements=elements,
        wave_vectors=wave_vectors,
        snr=snr,
        samplerate=samplerate,
        num_channels=channels,
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

    # MUSIC
    matrix = SteeringMatrix(
        elements=elements,
        azimuths=np.array([0]),
        inclanations=np.arange(-np.pi, np.pi, delta_theta),
        wavenumber=wave_number,
        wave_speed=343
    )
    array.array_to_csv(matrix.matrix, "arbitrary.csv")

    # matrix = OneDimensionalArray(spacing, channels, delta_theta)
    # array.array_to_csv(matrix.matrix, "uniform.csv")

    music = direction_of_arrival.MUSIC(matrix, num_sources=4)

    # Plotter
    app = QtWidgets.QApplication([])
    plot = plotters.SingleLinePlotter(
        title='MUSIC',
        x_label='Angle',
        y_label='Power',
        blocksize=1000,
        x_data=np.linspace(-90, 90, int(2 * np.pi / delta_theta + 0.5)),
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
