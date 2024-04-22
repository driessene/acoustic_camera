import AccCam.realtime_dsp as dsp
import AccCam.direction_of_arival as doa
from matplotlib.pyplot import show
import numpy as np


def main():

    # Variables
    samplerate = 44100
    blocksize = 44100
    wave_number = 1.46
    speed_of_sound = 343
    snr = 50
    channels = 8
    sleep = False

    # Sources
    elements = [
        doa.Element([0.00, 0, 0]),
        doa.Element([0.25, 0, 0]),
        doa.Element([0.50, 0, 0]),
        doa.Element([0.75, 0, 0]),
        doa.Element([1.00, 0, 0]),
        doa.Element([1.25, 0, 0]),
        doa.Element([1.50, 0, 0]),
        doa.Element([1.75, 0, 0])
    ]

    wave_vectors = [
        doa.WaveVector([wave_number * 1.0, 0, np.deg2rad(10)], speed_of_sound),
        doa.WaveVector([wave_number * 1.2, 0, np.deg2rad(50)], speed_of_sound)
    ]

    # Recorder to get data
    recorder = doa.AudioSimulator(
        elements=elements,
        wave_vectors=wave_vectors,
        snr=snr,
        samplerate=samplerate,
        blocksize=blocksize,
        sleep=sleep
    )

    # Filter
    filt = doa.FIRWINFilter(
        N=101,
        num_channels=channels,
        cutoff=2000,
        samplerate=samplerate,
        method='filtfilt',
    )

    # FFT
    fft_channel = dsp.ChannelPicker(0)
    fft = dsp.FFT(return_abs=True)

    # Plotter
    delta_f = blocksize / samplerate

    plot = dsp.LinePlotter(
        title='FFT',
        x_label='K',
        y_label='Abs Value',
        num_lines=1,
        num_points=blocksize,
        y_extent=[0, 100],
        interval=blocksize / samplerate
    )

    # Linking
    recorder.link_to_destination(filt, 0)
    filt.link_to_destination(fft_channel, 0)
    fft_channel.link_to_destination(fft, 0)
    fft.link_to_destination(plot, 0)

    # Start processes
    recorder.start()
    filt.start()
    fft_channel.start()
    fft.start()
    plot.start()
    show()


if __name__ == '__main__':
    main()

