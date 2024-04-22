import AccCam.realtime_dsp as dsp
import AccCam.direction_of_arival as doa
import numpy as np


def main():

    # Variables

    samplerate = 44100
    blocksize = 1024
    wave_number = 10
    speed_of_sound = 343

    # Sources
    elements = [doa.Element([-1.25, 0, 0]),
                doa.Element([-0.75, 0, 0]),
                doa.Element([-0.25, 0, 0]),
                doa.Element([0.25, 0, 0]),
                doa.Element([0.75, 0, 0]),
                doa.Element([1.25, 0, 0]),
                doa.Element([0, -1.25, 0]),
                doa.Element([0, -0.75, 0]),
                doa.Element([0, -0.25, 0]),
                doa.Element([0, 0.25, 0]),
                doa.Element([0, 0.75, 0]),
                doa.Element([0, 1.25, 0]),
                doa.Element([0, 0, 0.25]),
                doa.Element([0, 0, 0.75]),
                doa.Element([0, 0, 1.25])]

    wave_vectors = [
        doa.WaveVector(doa.spherical_to_cartesian(np.array([wave_number * 1.00, 1, 1])), speed_of_sound),
        doa.WaveVector(doa.spherical_to_cartesian(np.array([wave_number * 1.02, 2, 2])), speed_of_sound),
    ]

    # Print frequency for debuging
    for wave in wave_vectors:
        print(wave.linear_frequency)

    # Recorder to get data
    recorder = dsp.AudioSimulator(
        elements=elements,
        wave_vectors=wave_vectors,
        snr=50,
        samplerate=samplerate,
        blocksize=blocksize,
        sleep=True
    )

    # Filter
    filt = dsp.FIRWINFilter(
        N=101,
        num_channels=len(elements),
        cutoff=2000,
        samplerate=samplerate,
        method='filtfilt',
    )

    # Plot
    plot = dsp.LinePlotter(
        title='Audio Waves',
        x_label="N",
        y_label="Amplitude",
        num_lines=len(elements),
        num_points=blocksize,
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
    plot.show()


if __name__ == '__main__':
    main()
