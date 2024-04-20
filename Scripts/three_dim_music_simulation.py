import DSP
import Geometry
import numpy as np
from sys import getsizeof


def main():

    # Variables
    samplerate = 44100
    blocksize = 1024
    wave_number = 10
    speed_of_sound = 343

    elements = [Geometry.Element([-1.25, 0, 0]),
                Geometry.Element([-0.75, 0, 0]),
                Geometry.Element([-0.25, 0, 0]),
                Geometry.Element([0.25, 0, 0]),
                Geometry.Element([0.75, 0, 0]),
                Geometry.Element([1.25, 0, 0]),
                Geometry.Element([0, -1.25, 0]),
                Geometry.Element([0, -0.75, 0]),
                Geometry.Element([0, -0.25, 0]),
                Geometry.Element([0, 0.25, 0]),
                Geometry.Element([0, 0.75, 0]),
                Geometry.Element([0, 1.25, 0]),
                Geometry.Element([0, 0, 0.25]),
                Geometry.Element([0, 0, 0.75]),
                Geometry.Element([0, 0, 1.25])]

    wave_vectors = [
        Geometry.WaveVector(Geometry.spherical_to_cartesian(np.array([wave_number * 1.00, 1, 1])), speed_of_sound),
        Geometry.WaveVector(Geometry.spherical_to_cartesian(np.array([wave_number * 1.02, 2, 2])), speed_of_sound),
    ]

    # Print frequencies for debug
    for vector in wave_vectors:
        print(vector.linear_frequency)

    # Recorder to get data
    recorder = DSP.AudioSimulator(
        elements=elements,
        wave_vectors=wave_vectors,
        snr=50,
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
    azimuth_angles = np.linspace(0, 2 * np.pi, 1000)
    inclination_angles = np.linspace(0, np.pi, 1000)
    matrix = Geometry.SteeringMatrix(
        elements=elements,
        azimuths=azimuth_angles,
        inclinations=inclination_angles,
        wavenumber=wave_number,
    )
    print(matrix.matrix.shape)
    print(getsizeof(matrix))
    music = DSP.MUSIC(
        steering_matrix=matrix,
        num_sources=4
    )

    # Plot
    plot = DSP.ThreeDimPlotter(
        title='MUSIC',
        x_label="inclination",
        y_label="azimuth",
        x_data=inclination_angles,
        y_data=azimuth_angles,
        interval=blocksize/samplerate,
        z_extent=(0, 1)
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
