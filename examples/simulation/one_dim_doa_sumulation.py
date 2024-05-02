import AccCam.realtime_dsp as dsp
import AccCam.direction_of_arrival as doa
import numpy as np


def main():

    # Variables
    samplerate = 44100
    blocksize = 44100
    wavenumber = 12.3
    speed_of_sound = 343

    elements = [doa.Element(np.array([-1.25, 0, 0]), samplerate),
                doa.Element(np.array([-0.75, 0, 0]), samplerate),
                doa.Element(np.array([-0.25, 0, 0]), samplerate),
                doa.Element(np.array([0.25, 0, 0]), samplerate),
                doa.Element(np.array([0.75, 0, 0]), samplerate),
                doa.Element(np.array([1.25, 0, 0]), samplerate),
                ]

    structure = doa.Structure(
        elements=elements,
        wavenumber=wavenumber,
        snr=50,
        blocksize=blocksize,
        azimuth_range=(0, 0),
        azimuth_resolution=1,
        inclination_range=(0, np.pi),
        inclination_resolution=100
    )
    structure.visualize()

    wavevectors = [
        doa.WaveVector(doa.spherical_to_cartesian(np.array([wavenumber * 0.98, np.deg2rad(50), 0])), speed_of_sound),
    ]

    # Print frequencies for debug
    for vector in wavevectors:
        print(vector.linear_frequency)

    # Recorder to get data
    recorder = dsp.AudioSimulator(
        structure=structure,
        wavevectors=wavevectors
    )

    # Filter
    filt = dsp.FirwinFilter(
        n=1001,
        num_channels=len(elements),
        cutoff=np.array([400, 800]),
        type='bandpass',
        samplerate=samplerate,
        method='filtfilt',
        normalize=True,
        remove_offset=True
    )

    # MUSIC
    estimator = doa.MVDRBeamformer(structure)

    music = dsp.DOAEstimator(estimator)

    # Plot
    plot = dsp.PolarPlotter(
        title='MUSIC',
        num_points=structure.inclination_resolution,
        num_lines=1,
        interval=blocksize/samplerate,
        theta_data=structure.inclination_values,
        radius_extent=(0, 1)
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
