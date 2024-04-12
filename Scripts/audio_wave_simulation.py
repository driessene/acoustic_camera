from DSP.Sinks import plotters
from DSP.Processes import filters
from DSP.Sources import simulators
from Geometry.geometry import Element, WaveVector
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
    spacing = np.arange(0, 4, 0.5)
    elements = [Element([i, j, 0]) for (i, j) in product(spacing, spacing)]

    wave_vectors = [
        WaveVector([wave_number * 1.0, 1.0 * np.pi / 4, 1.0 * np.pi / 4], speed_of_sound),
        WaveVector([wave_number * 1.1, 1.1 * np.pi / 4, 1.3 * np.pi / 4], speed_of_sound)
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
        cutoff=1500,
        samplerate=samplerate,
        method='filtfilt',
    )

    # Plot
    plot = plotters.LinePlotter(
        title='Audio Waves',
        x_label="N",
        y_label="Amplitude",
        num_lines=len(elements),
        num_points=blocksize,
        x_extent=[100, 500],
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
