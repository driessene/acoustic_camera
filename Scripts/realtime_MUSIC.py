from DSP import direction_of_arrival, filters, plotters, recorders
import matplotlib.pyplot as plt


def main():
    plotter = plotters.LinePlotter(xlim=(-90, 90), ylim=(0, 1), interval=1000 * 512 / 44100)
    music = direction_of_arrival.MUSIC((plotter.in_queue,), spacing=0.5, num_mics=6, num_sources=2)
    hanning = filters.HanningWindow((music.in_queue,))
    fir = filters.FIRWINFilter((hanning.in_queue,), N=100, cutoff=1200, type='filtfilt')
    recorder = recorders.AudioRecorder(
        destinations=(fir.in_queue,),
        device_id=14,
        samplerate=44100,
        channels=8,
        blocksize=512,
        queue_size=2
    )

    recorder.start()
    fir.start()
    hanning.start()
    music.start()
    plt.show()


if __name__ == '__main__':
    main()