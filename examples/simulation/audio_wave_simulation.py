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
                doa.Element(np.array([0, 1.25, 0]), samplerate),
                doa.Element(np.array([0, 0, 0.25]), samplerate),
                doa.Element(np.array([0, 0, 0.75]), samplerate),
                doa.Element(np.array([0, 0, 1.25]), samplerate)]

    structure = doa.Structure(
        elements=elements,
        wavenumber=wavenumber,
        snr=50,
        blocksize=blocksize,
    )
    structure.visualize()

    n = list(range(1, 21))
    freq_scale = [2 * i - 1 for i in n]
    powr_scale = [1 / i for i in freq_scale]

    wavevectors = [
        doa.WaveVector(doa.spherical_to_cartesian(np.array([wavenumber * fs, 1, 1])), power=ps) for
        (fs, ps) in zip(freq_scale, powr_scale)
    ]

    # Print frequency for debugging
    for wave in wavevectors:
        print(wave.linear_frequency)

    # Recorder to get data
    recorder = dsp.AudioSimulator(
        structure=structure,
        wavevectors=wavevectors,
        randomize_phase=False
    )

    # Plot
    plot = dsp.LinePlotter(
        title='Audio Waves',
        x_label="N",
        y_label="Amplitude",
        num_lines=len(elements),
        num_points=blocksize,
        y_extent=(-1, 1),
        x_extent=(1000, 1500),
        interval=blocksize/samplerate
    )

    # Linking
    recorder.link_to_destination(plot, 0)

    # Start processes
    recorder.start()
    plot.start()
    plot.show()


if __name__ == '__main__':
    main()
