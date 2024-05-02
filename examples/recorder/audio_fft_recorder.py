import AccCam.realtime_dsp as dsp
import AccCam.direction_of_arrival as doa
from matplotlib.pyplot import show
import numpy as np


def main():

    # Variables
    samplerate = 44100
    blocksize = 44100
    wavenumber = 12.3

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

    test_wavevector = doa.WaveVector(doa.spherical_to_cartesian(np.array([wavenumber, 0, 0])), 343)
    print(test_wavevector.linear_frequency)

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
        n=501,
        num_channels=len(elements),
        cutoff=np.array([1, 300, 1000, samplerate / 2 - 1]),
        samplerate=samplerate,
        method='filtfilt',
        normalize=True,
        remove_offset=True
    )
    filt.plot_response()

    # hanning
    hanning = dsp.HanningWindow()

    # fft
    fft = dsp.FFT('abs')

    # Plot
    plot = dsp.LinePlotter(
        title='fft',
        x_label="hz",
        y_label="power",
        num_lines=len(elements),
        num_points=blocksize,
        interval=blocksize/samplerate,
        x_extent=(0, 2000),
        y_extent=(0, 1e7),
        x_data=np.fft.fftfreq(blocksize, 1/samplerate),
        legend=True
    )

    # Linking
    recorder.link_to_destination(hanning, 0)
    hanning.link_to_destination(filt, 0)
    filt.link_to_destination(fft, 0)
    fft.link_to_destination(plot, 0)


    # Start processes
    recorder.start()
    hanning.start()
    fft.start()
    filt.start()
    plot.start()
    show()


if __name__ == '__main__':
    main()
