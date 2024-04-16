import DSP
import Geometry
import numpy as np
from itertools import product


def main():

    # Variables
    samplerate = 44100
    blocksize = 1024
    wave_number = 2
    speed_of_sound = 343

    # ELEMENTS
    # sphere
    elements = [Geometry.Element(Geometry.spherical_to_cartesian(np.array([1, theta, phi]))) for (theta, phi)
                in product(np.linspace(0, np.pi, 5), np.linspace(0, 2 * np.pi, 10))]

    # Box
    # elements = [Geometry.Element([x, y, z]) for (x, y, z) in
    #             product(np.arange(0, 4, 0.5), np.arange(0, 4, 0.5), np.arange(0, 4, 0.5))]

    # +
    # elements = [Geometry.Element([-1.25, 0, 0]),
    #             Geometry.Element([-0.75, 0, 0]),
    #             Geometry.Element([-0.25, 0, 0]),
    #             Geometry.Element([0.25, 0, 0]),
    #             Geometry.Element([0.75, 0, 0]),
    #             Geometry.Element([1.25, 0, 0]),
    #             Geometry.Element([0, -1.25, 0]),
    #             Geometry.Element([0, -0.75, 0]),
    #             Geometry.Element([0, -0.25, 0]),
    #             Geometry.Element([0, 0.25, 0]),
    #             Geometry.Element([0, 0.75, 0]),
    #             Geometry.Element([0, 1.25, 0]),
    #             Geometry.Element([0, 0, 0.25]),
    #             Geometry.Element([0, 0, 0.75]),
    #             Geometry.Element([0, 0, 1.25])]

    wave_vectors = [
        Geometry.WaveVector([wave_number * 1.00, np.pi / 2.5, np.pi / 2.5], speed_of_sound),
        Geometry.WaveVector([wave_number * 1.02, np.pi / 3.5, np.pi / 3.5], speed_of_sound),
        Geometry.WaveVector([wave_number * 1.04, np.pi / 4.5, np.pi / 4.5], speed_of_sound)
    ]

    # Print frequencies for debugging
    for vect in wave_vectors:
        print(vect.frequency)

    # Recorder to get data
    recorder = DSP.AudioSimulator(
        elements=elements,
        wave_vectors=wave_vectors,
        snr=20,
        samplerate=samplerate,
        blocksize=blocksize,
        sleep=True
    )

    # Filter
    filt = DSP.FIRWINFilter(
        N=101,
        num_channels=len(elements),
        cutoff=2000,
        samplerate=samplerate,
        method='filtfilt',
    )

    # MUSIC
    azimuth_angles = np.linspace(0, 2 * np.pi, 500)
    inclination_angles = np.linspace(0, np.pi, 500)
    matrix = Geometry.SteeringMatrix(
        elements=elements,
        azimuths=azimuth_angles,
        inclinations=inclination_angles,
        wavenumber=wave_number,
    )
    music = DSP.MUSIC(
        steering_matrix=matrix,
        num_sources=6
    )

    # Plot
    plot = DSP.ThreeDimPlotter(
        title='MUSIC',
        x_label="inclination",
        y_label="azimuth",
        x_data=inclination_angles,
        y_data=azimuth_angles,
        interval=blocksize/samplerate,
        z_extent=(0, 0.5)
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
