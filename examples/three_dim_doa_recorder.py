import AccCam.realtime_dsp as dsp
import AccCam.direction_of_arrival as doa
import numpy as np


def main():

    # Variables
    samplerate = 44100
    blocksize = 44100
    wavenumber = 10

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
                doa.Element(np.array([0, 1.25, 0]), samplerate)]

    structure = doa.Structure(
        elements=elements,
        wavenumber=wavenumber,
        snr=50,
        blocksize=blocksize,
    )
    # structure.visualize()

    # Recorder to get data
    dsp.print_audio_devices()
    recorder_x = dsp.AudioRecorder(
        device_id=23,
        samplerate=44100,
        num_channels=8,
        blocksize=blocksize,
        channel_map=[2, 3, 4, 5, 6, 7],
    )
    recorder_y = dsp.AudioRecorder(
        device_id=24,
        samplerate=44100,
        num_channels=8,
        blocksize=blocksize,
        channel_map=[2, 3, 4, 5, 6, 7],
    )

    # Combine recorders
    concat = dsp.Concatenator(
        num_ports=2,
    )

    # Filter
    filt = dsp.FIRWINFilter(
        n=101,
        num_channels=len(elements),
        cutoff=1000,
        samplerate=samplerate,
        method='filtfilt',
    )

    # MUSIC
    estimator = doa.Music(structure, 2)
    doa_stage = dsp.DOAEstimator(estimator)

    # Plot
    plot = dsp.HeatmapPlotter(
        title='MUSIC',
        x_label="inclination",
        y_label="azimuth",
        x_data=structure.inclination_values,
        y_data=structure.azimuths_values,
        interval=blocksize/samplerate
    )

    # Linking
    recorder_x.link_to_destination(concat, 0)
    recorder_y.link_to_destination(concat, 1)
    concat.link_to_destination(filt, 0)
    filt.link_to_destination(doa_stage, 0)
    doa_stage.link_to_destination(plot, 0)

    # Start processes
    recorder_x.start()
    recorder_y.start()
    concat.start()
    filt.start()
    doa_stage.start()
    plot.start()
    plot.show()


if __name__ == '__main__':
    main()
