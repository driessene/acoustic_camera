from DSP import pipeline, plotters, filters, recorders, direction_of_arrival
from realtime_MUSIC import RTMUSIC


def main():
    # Components
    recorder = recorders.AudioSimulator(
        frequencies=[675, 500],
        doas=[10, 30],
        spacing=0.254,
        snr=50,
        samplerate=44100,
        channels=6,
        blocksize=1024,
        queue_size=2,
    )
    fs = [filters.FIRWINFilter(300, 1000), filters.HanningFilter()]

    fs[0].plot_response()

    doa = direction_of_arrival.MUSIC(
        spacing=0.5,
        test_angles=1000,
        num_mics=6,
        num_sources=2
    )
    wave_plotter = plotters.MultiLinePlotter(xlim=(0, 512), ylim=(-1, 1), lines=6, interval=1000 * 512 / 44100)
    music_plotter = plotters.LinePlotter(xlim=(-90, 90), ylim=(0, 1), interval=1000 * 512 / 44100)

    # Pipeline
    pipe = RTMUSIC(
        recorder=recorder,
        filters=fs,
        music=doa,
        plotters=[wave_plotter, music_plotter]
    )
    pipe.start()

if __name__ == '__main__':
    main()
