from DSP.Sinks import plotters
from DSP.Processes import direction_of_arrival, filters
from DSP.Sources import simulators
from Geometry.arbitrary import SteeringMatrix, Element, WaveVector
from Geometry.uniform import OneDimensionalArray
from pyqtgraph.Qt import QtWidgets
import numpy as np


def main():

    # Variables
    samplerate = 44100
    blocksize = 44100
    wave_number = 3.94  # 10 inches
    speed_of_sound = 343
    snr = 50
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
        WaveVector([wave_number, 0, 0.175], speed_of_sound),   # 10 deg
        WaveVector([wave_number, 0, 0.873], speed_of_sound)    # 50 deg
    ]

    # Recorder to get data
    recorder = simulators.AudioSimulator(
        elements=elements,
        wave_vectors=wave_vectors,
        snr=snr,
        samplerate=samplerate,
        num_channels=len(elements),
        blocksize=blocksize,
        sleep=sleep
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
    matrix = SteeringMatrix(
        elements=elements,
        azimuths=np.array([0]),
        inclinations=np.arange(-np.pi/2, np.pi/2, delta_theta),
        wave_speed=speed_of_sound,
        wavenumber=wave_vectors
    )
    music = direction_of_arrival.MUSIC(matrix, num_sources=4)

    # Plotter
    app = QtWidgets.QApplication([])
    plot = plotters.SingleLinePlotter(
        title='MUSIC',
        x_label='Angle',
        y_label='Power',
        blocksize=1000,
        x_data=np.linspace(-90, 90, int(np.pi / delta_theta + 0.5)),
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
