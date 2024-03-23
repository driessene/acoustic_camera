import sounddevice as sd
from Management import pipeline


class AudioPlayback(pipeline.Stage):
    """
    Plays audio from a numpy array. Expects a matrix of multiple channels like the rest of this project.
    """
    def __init__(self, samplerate=44100, blocksize=1024, channel=0, queue_size=4):
        """
        Initialize the audio playback
        :param samplerate: The samplerate of the recorder
        :param blocksize: The number of samples per block of audio
        :param channel: The channel from the signal matrix to play back
        :param queue_size: The size of the input queue
        """
        super().__init__(1, queue_size, None, has_process=False)

        self.samplerate = samplerate
        self.blocksize = blocksize
        self.channel = channel
        self.stream = None

    def _audio_callback(self, outdata, frames, time, status):
        """
        Called by sounddevice. Called for every block of audio data
        :param outdata: Data to the player
        :param frames: Data to output devices. Not used
        :param time: Time of the recorder. Not used
        :param status: Error status of the recorder. If error, print it
        :return: None
        """
        if status:
            print(status)

        outdata[:, 0] = self.input_queue_get()[0][:, self.channel]

    def start(self):
        """
        Starts the playback stream. Must be called by a script at least once
        :return: None
        """
        self.stream = sd.OutputStream(
            samplerate=self.samplerate,
            blocksize=self.blocksize,
            callback=self._audio_callback,
            channels=1
        )
        self.stream.start()

    def stop(self):
        """
        Stops the playback stream
        :return:
        """
        if self.stream:
            self.stream.stop()
            self.stream.close()
