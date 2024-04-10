from DSP.Sinks import plotters
from DSP.Processes import filters, direction_of_arrival
from DSP.Sources import simulators
from Geometry.arbitrary import Element, WaveVector, SteeringMatrix
from matplotlib.pyplot import show
import numpy as np
from itertools import product


def main():

    # Variables
    samplerate = 44100
    blocksize = 1024
    wave_number = 2
    speed_of_sound = 343

    # Sources
    spacing = np.arange(0, 4, 0.5)
    elements = [Element([i, j, k]) for (i, j, k) in product(spacing, spacing, spacing)]

    wave_vectors = [
        WaveVector([wave_number * 1.0, 1.0 * np.pi / 4, 1.0 * np.pi / 4], speed_of_sound),
        WaveVector([wave_number * 1.1, 1.1 * np.pi / 4, 1.3 * np.pi / 4], speed_of_sound)
    ]

    # Recorder to get data
    recorder = simulators.AudioSimulator(
        elements=elements,
        wave_vectors=wave_vectors,
        snr=50,
        samplerate=samplerate,
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
    azimuth_angles = np.linspace(0, 2 * np.pi, 100)
    inclination_angles = np.linspace(0, np.pi, 100)
    matrix = SteeringMatrix(
        elements=elements,
        azimuths=azimuth_angles,
        inclinations=inclination_angles,
        wavenumber=wave_number,
        wave_speed=speed_of_sound
    )
    music = direction_of_arrival.MUSIC(
        steering_matrix=matrix,
        num_sources=len(wave_vectors) * 2
    )
    # Plot
    plot = plotters.ThreeDimPlotter(
        title='MUSIC',
        x_label="inclination",
        y_label="azimuth",
        x_data=inclination_angles,
        y_data=azimuth_angles,
        interval=blocksize/samplerate
    )
    # Linking
    recorder.link_to_destination(filt, 0)
    filt.link_to_destination(music, 0)
    music.link_to_destination(plot, 0)

    # Start processes
    recorder.start()
    filt.start()
    music.start()
    plot.start()
    show()


if __name__ == '__main__':
    main()
