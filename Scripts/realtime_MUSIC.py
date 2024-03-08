from DSP import pipeline, plotters, filters, recorders, direction_of_arrival

class RTMUSIC(pipeline.AudioPipeline):
    def __init__(self,
                 recorder: recorders,
                 filters: list[filters],
                 music: direction_of_arrival.MUSIC,
                 plotters: list[plotters]):  # One plot for waveforms, one for music
        super(RTMUSIC, self).__init__(recorder, filters, [music], plotters)


    def flowpath(self):
        # Get data
        data = self.recorder.pop()

        # Apply filters in order
        for f in self.filters:
            data = f.process(data)

        # Apply MUSIC
        music = self.dsp_algorithms[0].process(data)

        # Plot
        self.plotters[0].set_data(data)
        self.plotters[1].set_data(music)


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
    fs = [filters.FIRWINFilter(11, 2000), filters.HanningFilter()]
    doa = direction_of_arrival.MUSIC(
        spacing=0.5,
        test_angles=1000,
        num_mics=6,
        num_sources=1
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
