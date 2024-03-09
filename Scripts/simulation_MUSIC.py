from DSP import recorders, filters, direction_of_arrival, plotters
import matplotlib.pyplot as plt


def main():
    # Components
    recorder = recorders.AudioSimulator(
        frequencies=(675, 500),
        doas=(10, 30),
        spacing=0.254,
        snr=50,
        samplerate=44100,
        channels=6,
        blocksize=1024,
        sleep=False
    )
    fir = filters.FIRWINFilter(recorder.out_queue, N=100, cutoff=1200, type='filtfilt')
    hanning = filters.HanningWindow(fir.out_queue)
    music = direction_of_arrival.MUSIC(hanning.out_queue, spacing=0.5, num_mics=6, num_sources=2)
    plotter = plotters.LinePlotter(music.out_queue, xlim=(-90, 90), ylim=(0, 1), interval=1000 * 512 / 44100)

    recorder.start()
    fir.start()
    hanning.start()
    music.start()
    plt.show()


if __name__ == '__main__':
    main()
