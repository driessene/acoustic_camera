from AccCam.__config__ import __USE_CUPY__

if __USE_CUPY__:
    import cupy as np
else:
    import numpy as np

import AccCam.realtime_dsp as dsp
import AccCam.direction_of_arrival as doa


def main():

    # Variables
    samplerate = 44100
    blocksize = 44100
    wavenumber = 12.3

    # Sphere
    elements = [doa.Element(np.array([-1.25, 0, 0]), samplerate),
                doa.Element(np.array([-0.75, 0, 0]), samplerate),
                doa.Element(np.array([-0.25, 0, 0]), samplerate),
                doa.Element(np.array([0.25, 0, 0]), samplerate),
                doa.Element(np.array([0.75, 0, 0]), samplerate),
                doa.Element(np.array([1.25, 0, 0]), samplerate),
                doa.Element(np.array([0, -1.25, 0]), samplerate),
                doa.Element(np.array([0, -0.75, 0]), samplerate),
                doa.Element(np.array([0, -0.25, 0]), samplerate),
                doa.Element(np.array([0, 0.25, 0]), samplerate),
                doa.Element(np.array([0, 0.75, 0]), samplerate),
                doa.Element(np.array([0, 1.25, 0]), samplerate)]

    structure = doa.Structure(
        elements=elements,
        wavenumber=wavenumber,
        snr=5,
        blocksize=blocksize,
    )
    structure.visualize()

    wavevectors = [
        doa.WaveVector(doa.spherical_to_cartesian(np.array([wavenumber * 0.98, 1, 1]))),
        doa.WaveVector(doa.spherical_to_cartesian(np.array([wavenumber * 1.02, 2, 2]))),
    ]

    # Print frequencies for debug
    for vector in wavevectors:
        print(vector.linear_frequency)

    # Print ideal spacing
    for vector in wavevectors:
        print(vector.linear_wavelength / 2)

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
    filt.plot_response()

    # Hanning window
    hanning = dsp.HanningWindow()

    # FFT
    spect = dsp.FFT(type='power')
    freqs = np.fft.fftfreq(blocksize, 1/samplerate)
    print(freqs)

    # Plot
    plot = dsp.LinePlotter(
        title='Spectral Power',
        x_label='Hz',
        y_label='Power',
        num_points=blocksize,
        num_lines=len(structure.elements),
        interval=blocksize/samplerate,
        legend=True,
        x_data=freqs,
        x_extent=(-10000, 10000),
        y_extent=(0, 10000)
    )

    # Linking
    recorder.link_to_destination(filt, 0)
    filt.link_to_destination(hanning, 0)
    hanning.link_to_destination(spect, 0)
    spect.link_to_destination(plot, 0)

    # Start processes
    recorder.start()
    filt.start()
    hanning.start()
    spect.start()
    plot.start()
    plot.show()


if __name__ == '__main__':
    main()
