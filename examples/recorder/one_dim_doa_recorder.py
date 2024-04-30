import AccCam.realtime_dsp as dsp
import AccCam.direction_of_arrival as doa
import numpy as np


def main():

    # Variables
    samplerate = 44100
    blocksize = 1024
    wavenumber = 10
    speed_of_sound = 343

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

    wavevectors = [
        doa.WaveVector(doa.spherical_to_cartesian(np.array([wavenumber * 0.98, 1, 1])), speed_of_sound),
        doa.WaveVector(doa.spherical_to_cartesian(np.array([wavenumber * 1.02, 2, 2])), speed_of_sound),
    ]

    # Print frequencies for debug
    for vector in wavevectors:
        print(vector.linear_frequency)

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
        n=101,
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
        y_extent=(-1, 1),
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
