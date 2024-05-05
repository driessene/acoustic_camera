from AccCam.__config__ import __USE_CUPY__

if __USE_CUPY__:
    import cupy as np
else:
    import numpy as np

import AccCam.realtime_dsp as dsp
import AccCam.direction_of_arrival as doa
import AccCam.visual as vis


def main():

    # Variables
    samplerate = 44100
    blocksize = 44100
    wavenumber = 12.3
    speed_of_sound = 343

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
                doa.Element(np.array([0, 1.25, 0]), samplerate),
                doa.Element(np.array([0, 0, 0.25]), samplerate),
                doa.Element(np.array([0, 0, 0.75]), samplerate),
                doa.Element(np.array([0, 0, 1.25]), samplerate)]

    structure = doa.Structure(
        elements=elements,
        wavenumber=wavenumber,
        snr=50,
        blocksize=blocksize
    )
    # structure.visualize()

    wavevectors = [
        doa.WaveVector(doa.spherical_to_cartesian(np.array([wavenumber * 0.98, 1, 1])), speed_of_sound),
        doa.WaveVector(doa.spherical_to_cartesian(np.array([wavenumber * 1.02, 2, 2])), speed_of_sound),
    ]

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

    camera = vis.Camera((500, 500), (0, np.pi), (0, 2 * np.pi), video_source=0)

    # Plot
    plot = dsp.HeatmapPlotterVideo(
        structure=structure,
        camera=camera,
        title='MUSIC',
        x_label="inclination",
        y_label="azimuth",
        x_len=structure.inclination_resolution,
        y_len=structure.azimuth_resolution,
        interval=blocksize/samplerate,
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
