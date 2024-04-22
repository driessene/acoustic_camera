import DSP
import Geometry
import Pipeline
import numpy as np


def main():

    # Variables
    samplerate = 44100
    blocksize = 1024
    wave_number = 2
    speed_of_sound = 343

    # Sources
    elements = [Geometry.Element([-1.25, 0, 0]),
                Geometry.Element([-0.75, 0, 0]),
                Geometry.Element([-0.25, 0, 0]),
                Geometry.Element([0.25, 0, 0]),
                Geometry.Element([0.75, 0, 0]),
                Geometry.Element([1.25, 0, 0]),
                Geometry.Element([0, -1.25, 0]),
                Geometry.Element([0, -0.75, 0]),
                Geometry.Element([0, -0.25, 0]),
                Geometry.Element([0, 0.25, 0]),
                Geometry.Element([0, 0.75, 0]),
                Geometry.Element([0, 1.25, 0])]

    wave_vectors = [
        Geometry.WaveVector([wave_number * 1.0, 1.0 * np.pi / 4, 1.0 * np.pi / 4], speed_of_sound),
        Geometry.WaveVector([wave_number * 1.1, 1.1 * np.pi / 4, 1.3 * np.pi / 4], speed_of_sound)
    ]

    # Recorder to get data
    recorder = DSP.AudioSimulator(
        elements=elements,
        wave_vectors=wave_vectors,
        snr=50,
        samplerate=samplerate,
        blocksize=blocksize,
        sleep=False
    )

    # Combine recorders
    concat = Pipeline.Concatenator(
        num_ports=2,
    )

    # Filter
    filt = DSP.FIRWINFilter(
        N=101,
        num_channels=len(elements),
        cutoff=1000,
        samplerate=samplerate,
        method='filtfilt',
    )

    # Accumulate for 1 min
    accum = Pipeline.Accumulator(60 * samplerate / blocksize, axis=0)

    # Save
    save = Pipeline.ToDisk("simulator", "C:/Users/2020e/Desktop")

    # Linking
    recorder.link_to_destination(filt, 0)
    concat.link_to_destination(filt, 0)
    filt.link_to_destination(accum, 0)
    accum.link_to_destination(save, 0)

    # Start processes
    recorder.start()
    concat.start()
    filt.start()
    accum.start()
    save.start()


if __name__ == '__main__':
    main()
