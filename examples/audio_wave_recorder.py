from DSP import direction_of_arival
from matplotlib.pyplot import show


def main():

    # Variables
    samplerate = 44100
    blocksize = 8192

    # Sources
    elements = [DSP.Element([-1.25, 0, 0]),
                DSP.Element([-0.75, 0, 0]),
                DSP.Element([-0.25, 0, 0]),
                DSP.Element([0.25, 0, 0]),
                DSP.Element([0.75, 0, 0]),
                DSP.Element([1.25, 0, 0]),
                DSP.Element([0, -1.25, 0]),
                DSP.Element([0, -0.75, 0]),
                DSP.Element([0, -0.25, 0]),
                DSP.Element([0, 0.25, 0]),
                DSP.Element([0, 0.75, 0]),
                DSP.Element([0, 1.25, 0])]

    # Recorder to get data
    DSP.print_audio_devices()
    recorder_x = DSP.AudioRecorder(
        device_id=24,
        samplerate=44100,
        num_channels=8,
        blocksize=blocksize,
        channel_map=[2, 3, 4, 5, 6, 7],
    )
    recorder_y = DSP.AudioRecorder(
        device_id=23,
        samplerate=44100,
        num_channels=8,
        blocksize=blocksize,
        channel_map=[2, 3, 4, 5, 6, 7],
    )

    # Combine recorders
    concat = DSP.Concatenator(
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

    # Plot
    plot = DSP.LinePlotter(
        title='MUSIC',
        x_label="inclination",
        y_label="azimuth",
        num_lines=len(elements),
        num_points=blocksize,
        interval=blocksize/samplerate,
        x_extent=[0, blocksize],
        y_extent=[-1, 1],
        legend=True
    )

    # Linking
    recorder_x.link_to_destination(concat, 0)
    recorder_y.link_to_destination(concat, 1)
    concat.link_to_destination(filt, 0)
    filt.link_to_destination(plot, 0)

    # Start processes
    recorder_x.start()
    recorder_y.start()
    concat.start()
    filt.start()
    plot.start()
    show()


if __name__ == '__main__':
    main()
