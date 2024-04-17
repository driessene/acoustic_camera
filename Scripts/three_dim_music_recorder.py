import DSP
import Geometry
import Management
import numpy as np


def main():

    # Variables
    samplerate = 44100
    blocksize = 8192

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

    # Recorder to get data
    DSP.print_audio_devices()
    recorder_x = DSP.AudioRecorder(
        device_id=22,
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
    concat = Management.Concatenator(
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

    # MUSIC
    azimuth_angles = np.linspace(0, 2 * np.pi, 100)
    inclination_angles = np.linspace(0, np.pi, 100)
    matrix = Geometry.SteeringMatrix(
        elements=elements,
        azimuths=azimuth_angles,
        inclinations=inclination_angles,
        wavenumber=1.48,
    )
    music = DSP.MUSIC(
        steering_matrix=matrix,
        num_sources=2
    )

    # Plot
    plot = DSP.ThreeDimPlotter(
        title='MUSIC',
        x_label="inclination",
        y_label="azimuth",
        x_data=inclination_angles,
        y_data=azimuth_angles,
        interval=blocksize/samplerate
    )

    # Linking
    recorder_x.link_to_destination(concat, 0)
    recorder_y.link_to_destination(concat, 1)
    concat.link_to_destination(filt, 0)
    filt.link_to_destination(music, 0)
    music.link_to_destination(plot, 0)

    # Start processes
    recorder_x.start()
    recorder_y.start()
    concat.start()
    filt.start()
    music.start()
    plot.start()
    plot.show()


if __name__ == '__main__':
    main()
