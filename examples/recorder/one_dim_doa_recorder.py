import AccCam.realtime_dsp as dsp
import AccCam.direction_of_arrival as doa
import numpy as np


def main():

    # Variables
    samplerate = 44100
    blocksize = 44100
    wavenumber = 12.3

    elements = [doa.Element(np.array([-1.25, 0, 0]), samplerate),
                doa.Element(np.array([-0.75, 0, 0]), samplerate),
                doa.Element(np.array([-0.25, 0, 0]), samplerate),
                doa.Element(np.array([0.25, 0, 0]), samplerate),
                doa.Element(np.array([0.75, 0, 0]), samplerate),
                doa.Element(np.array([1.25, 0, 0]), samplerate)]

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

    # Get ideal frequency, print target frequency and spacing in inches
    test_wavevector = doa.WaveVector(doa.spherical_to_cartesian(np.array([wavenumber, 0, 0])), 343)
    print(test_wavevector.linear_frequency)
    print(test_wavevector.linear_wavelength * 39.3701 / 2)

    # Recorder to get data
    dsp.print_audio_devices()
    recorder = dsp.AudioRecorder(
        device_id=14,
        samplerate=44100,
        num_channels=8,
        blocksize=blocksize,
        channel_map=[2, 3, 4, 5, 6, 7]
    )

    # Filter
    filt = dsp.FirlsFilter(
        n=1001,
        num_channels=len(elements),
        bands=np.array([0, 399.99, 400, 800, 800.01, samplerate/2]),
        desired=np.array([0, 0, 1, 1, 0, 0]),
        samplerate=samplerate,
        method='filtfilt',
        normalize=True,
        remove_offset=True
    )
    filt.plot_response()

    # MUSIC
    estimator = doa.Music(structure, 2)

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
