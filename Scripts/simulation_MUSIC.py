from DSP import recorders, filters, direction_of_arrival, plotters
import matplotlib.pyplot as plt


def main():
    # Components
    plotter = plotters.LinePlotter(xlim=(-90, 90), ylim=(0, 1), interval=1000 * 512 / 44100)
    music = direction_of_arrival.MUSIC((plotter.in_queue,), spacing=0.5, num_mics=6, num_sources=2)
    hanning = filters.HanningWindow((music.in_queue,))
    fir = filters.FIRWINFilter((hanning.in_queue,), N = 100, cutoff = 1200, type = 'filtfilt')
    recorder = recorders.AudioSimulator(
        destinations=(fir.in_queue,),
        frequencies=(675, 500),
        doas=(10, 30),
        spacing=0.254,
        snr=50,
        samplerate=44100,
        channels=6,
        blocksize=1024,
        sleep=False
    )

    recorder.start()
    fir.start()
    hanning.start()
    music.start()
    plt.show()


if __name__ == '__main__':
    main()
