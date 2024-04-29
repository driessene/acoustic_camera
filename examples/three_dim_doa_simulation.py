import AccCam.realtime_dsp as dsp
import AccCam.direction_of_arrival as doa
import numpy as np
from itertools import product


def main():

    # Variables
    samplerate = 44100
    blocksize = 1024
    wavenumber = 10
    speed_of_sound = 343

    # Sphere
    elements = [doa.Element(doa.spherical_to_cartesian(np.array([1, inclination, azimuth])), samplerate)
                for (inclination, azimuth) in
                product(np.linspace(0.1 * np.pi, 0.9 * np.pi, 5), np.linspace(0, 1.8 * np.pi, 10))]

    structure = doa.Structure(
        elements=elements,
        wavenumber=wavenumber,
        snr=50,
        blocksize=blocksize,
    )

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
        n=101,
        num_channels=len(elements),
        cutoff=2000,
        samplerate=samplerate,
        method='filtfilt',
    )

    # MUSIC
    estimator = doa.MVDRBeamformer(structure)

    music = dsp.DOAEstimator(estimator)

    # Plot
    plot = dsp.HeatmapPlotter(
        title='MUSIC',
        x_label="inclination",
        y_label="azimuth",
        x_data=structure.inclination_values,
        y_data=structure.azimuths_values,
        interval=blocksize/samplerate,
        cmap='inferno'
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
