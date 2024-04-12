from DSP.Sinks import plotters
from DSP.Processes import filters, direction_of_arrival
from DSP.Sources import simulators
from Geometry.geometry import Element, WaveVector, SteeringMatrix, spherical_to_cartesian
import numpy as np


def main():

    # Variables
    samplerate = 44100
    blocksize = 1024
    wave_number = 1.5
    speed_of_sound = 343

    # ELEMENTS
    # sphere
    # elements = [Element(spherical_to_cartesian(1, theta, phi)) for (theta, phi) in product(np.linspace(0, np.pi, 5), np.linspace(0, 2 * np.pi, 10))]

    # Box
    # elements = [Element([x, y, z]) for (x, y, z) in product(np.arange(0, 4, 0.5), np.arange(0, 4, 0.5), np.arange(0, 4, 0.5))]

    # +
    elements = [Element([-1.25, 0, 0]),
                Element([-0.75, 0, 0]),
                Element([-0.25, 0, 0]),
                Element([0.25, 0, 0]),
                Element([0.75, 0, 0]),
                Element([1.25, 0, 0]),
                Element([0, -1.25, 0]),
                Element([0, -0.75, 0]),
                Element([0, -0.25, 0]),
                Element([0, 0.25, 0]),
                Element([0, 0.75, 0]),
                Element([0, 1.25, 0]),
                Element([0, 0, 0.25]),
                Element([0, 0, 0.75]),
                Element([0, 0, 1.25])]

    wave_vectors = [
        WaveVector([wave_number * 1, np.pi / 3.5, np.pi / 2.5], speed_of_sound),
        WaveVector([wave_number * 1.05, np.pi / 2.5, np.pi / 3.5], speed_of_sound)
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
        cutoff=2000,
        samplerate=samplerate,
        method='filtfilt',
    )

    # MUSIC
    azimuth_angles = np.linspace(0, 2 * np.pi, 500)
    inclination_angles = np.linspace(0, np.pi, 500)
    matrix = SteeringMatrix(
        elements=elements,
        azimuths=azimuth_angles,
        inclinations=inclination_angles,
        wavenumber=wave_number,
    )
    music = direction_of_arrival.MUSIC(
        steering_matrix=matrix,
        num_sources=len(wave_vectors) * 4
    )

    # Plot
    plot = plotters.ThreeDimPlotter(
        title='MUSIC',
        x_label="azimuth",
        y_label="inclination",
        x_data=azimuth_angles,
        y_data=inclination_angles,
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
    plot.show()


if __name__ == '__main__':
    main()
