from AccCam.__config__ import __USE_CUPY__

if __USE_CUPY__:
    import cupy as np
else:
    import numpy as np

import AccCam.realtime_dsp as dsp
import AccCam.direction_of_arrival as doa
from matplotlib.pyplot import show


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
    )
    structure.visualize()

    test_wavevector = doa.WaveVector(doa.spherical_to_cartesian(np.array([wavenumber, 0, 0])), 343)
    print(test_wavevector.linear_frequency)

    # Recorder to get data
    dsp.print_audio_devices()
    recorder = dsp.AudioRecorder(
        device_id=14,
        samplerate=44100,
        num_channels=8,
        blocksize=blocksize,
        channel_map=[2, 3, 4, 5, 6, 7],
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
    filt.plot_response()

    # Plot
    plot = dsp.LinePlotter(
        title='MUSIC',
        x_label="inclination",
        y_label="azimuth",
        num_lines=len(elements),
        num_points=blocksize,
        interval=blocksize/samplerate,
        x_extent=(0, blocksize),
        y_extent=(-1, 1),
        legend=True
    )

    # Linking
    recorder.link_to_destination(filt, 0)
    filt.link_to_destination(plot, 0)

    # Start processes
    recorder.start()
    filt.start()
    plot.start()
    show()


if __name__ == '__main__':
    main()
