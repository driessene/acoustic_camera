from DSP.Sinks import plotters
from DSP.Processes import filters
from DSP.Sources import simulators
from Geometry.arbitrary import Element, WaveVector
from matplotlib.pyplot import show
import numpy as np
from itertools import product


def main():

    # Variables
    samplerate = 44100
    blocksize = 1024
    wave_number = 1.46
    speed_of_sound = 343

    # Sources
    elements = [Element([i, j, 1]) for (i, j) in product(np.arange(0, 2, 0.25), np.arange(0, 2, 0.25))]

    wave_vectors = [
        WaveVector([wave_number * 1.0, np.deg2rad(10), np.deg2rad(10)], speed_of_sound),
        WaveVector([wave_number * 1.1, np.deg2rad(50), np.deg2rad(50)], speed_of_sound)
    ]

    # Recorder to get data
    recorder = simulators.AudioSimulator(
        elements=elements,
        wave_vectors=wave_vectors,
        snr=50,
        samplerate=samplerate,
        blocksize=blocksize,
        sleep=True
    )

    # Filter
    filt = filters.FIRWINFilter(
        N=101,
        num_channels=len(elements),
        cutoff=1000,
        samplerate=samplerate,
        method='filtfilt',
    )

    # Plot
    plot = plotters_matplotlib.LinePlotter(
        title='Audio Waves',
        x_label="N",
        y_label="Amplitude",
        num_lines=len(elements),
        num_points=blocksize,
        x_extent=[0, 100],
        y_extent=[-1, 1],
        interval=blocksize/samplerate
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
