from DSP import direction_of_arrival, filters, plotters, recorders
from Management import pipeline


class MusicPipeline(pipeline.AudioPipeline):
    def __init__(self,
                 recorder: recorders,
                 filters: list[filters],
                 music: direction_of_arrival.MUSIC,
                 plotters: list[plotters]):  # One plot for waveforms, one for music
        super(MusicPipeline, self).__init__(recorder, filters, [music], plotters)

    def flowpath(self):
        # Get data
        data = self.recorder.out_queue_get()

        # Apply filters in order
        for f in self.filters:
            f.in_queue_put(data)
            data = f.out_queue_get()

        # Apply MUSIC
        self.algorithms[0].in_queue_put(data)
        music = self.algorithms[0].out_queue_get()

        # Plot
        self.plotters[0].in_queue_put(data)
        self.plotters[1].in_queue_put(music)


def main():
    # Print audio devices
    recorders.print_audio_devices()

    # Components
    recorder = recorders.AudioRecorder(
        device_id=14,
        samplerate=44100,
        channels=8,
        blocksize=512,
        queue_size=2
    )
    fs = [filters.FIRWINFilter(11, 2000), filters.HanningWindow()]
    doa = direction_of_arrival.MUSIC(
        spacing=0.5,
        test_angles=1000,
        num_mics=6,
        num_sources=1
    )
    wave_plotter = plotters.MultiLinePlotter(xlim=(0, 512), ylim=(-1, 1), lines=6, interval=1000 * 512 / 44100)
    music_plotter = plotters.LinePlotter(xlim=(-90, 90), ylim=(0, 1), interval=1000 * 512 / 44100)

    # Pipeline
    pipe = MusicPipeline(
        recorder=recorder,
        filters=fs,
        music=doa,
        plotters=[wave_plotter, music_plotter]
    )
    pipe.start()
