from DSP import source_simulators, filters, playback, plotters
from pyqtgraph.Qt import QtWidgets


def main():

    # Variables
    samplerate = 44100
    blocksize = 44100
    spacing = 0.254
    snr = 50
    channels = 8
    sleep = False

    # Sources
    sources = [source_simulators.Source(675, 10), source_simulators.Source(2000, 30)]

    # Recorder to get data
    recorder = source_simulators.AudioSimulator(
        sources=sources,
        spacing=spacing,
        snr=snr,
        samplerate=samplerate,
        channels=channels,
        blocksize=blocksize,
        sleep=sleep
    )

    # Filter
    filt = filters.FIRWINFilter(
        N=101,
        cutoff=1000,
        samplerate=44100,
        type='filtfilt',
    )

    # Playback
    play = playback.AudioPlayback(samplerate, blocksize)

    # Linking
    recorder.link_to_destination(filt, 0)
    filt.link_to_destination(play, 0)

    # Start processes
    recorder.start()
    filt.start()
    play.start()


if __name__ == '__main__':
    main()
