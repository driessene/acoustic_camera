import AccCam.realtime_dsp as dsp
import AccCam.direction_of_arival as doa
import numpy as np


def main():

    # Variables
    samplerate = 44100
    blocksize = 1024
    wave_number = 10
    speed_of_sound = 343

    elements = [doa.Element([-1.25, 0, 0]),
                doa.Element([-0.75, 0, 0]),
                doa.Element([-0.25, 0, 0]),
                doa.Element([0.25, 0, 0]),
                doa.Element([0.75, 0, 0]),
                doa.Element([1.25, 0, 0]),
                doa.Element([0, -1.25, 0]),
                doa.Element([0, -0.75, 0]),
                doa.Element([0, -0.25, 0]),
                doa.Element([0, 0.25, 0]),
                doa.Element([0, 0.75, 0]),
                doa.Element([0, 1.25, 0]),
                doa.Element([0, 0, 0.25]),
                doa.Element([0, 0, 0.75]),
                doa.Element([0, 0, 1.25])]

    wave_vectors = [
        doa.WaveVector(doa.spherical_to_cartesian(np.array([wave_number * 1.00, 1.2, 1.2])), speed_of_sound),
        #Geometry.WaveVector(Geometry.spherical_to_cartesian(np.array([wave_number * 1.02, 1.5, 1.5])), speed_of_sound),
    ]

    # Print frequencies for debug
    for vector in wave_vectors:
        print(vector.linear_frequency)

    # Recorder to get data
    recorder = dsp.AudioSimulator(
        elements=elements,
        wave_vectors=wave_vectors,
        snr=50,
        samplerate=samplerate,
        blocksize=blocksize,
        sleep=True
    )

    # Filter
    filt = dsp.FIRWINFilter(
        N=101,
        num_channels=len(elements),
        cutoff=2000,
        samplerate=samplerate,
        method='filtfilt',
    )

    # MUSIC
    azimuth_angles = np.linspace(0, 2 * np.pi, 500)
    inclination_angles = np.array([np.pi / 2])
    matrix = doa.SteeringMatrix(
        elements=elements,
        azimuths=azimuth_angles,
        inclinations=inclination_angles,
        wavenumber=wave_number,
    )

    music = dsp.MVDRBeamformer(
        steering_matrix=matrix,
    )

    # Plot
    plot = dsp.PolarPlotter(
        title='MUSIC',
        num_points=azimuth_angles.size,
        num_lines=1,
        interval=blocksize/samplerate,
        theta_data=azimuth_angles,
        radius_extent=[0, 1]
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
