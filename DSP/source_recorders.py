import sounddevice as sd
import numpy as np
from time import sleep
from Management import pipeline


def print_audio_devices():
    """
    Print all available audio devices
    :return: None
    """
    print("Microphone Devices:")
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            print(f"Device {i}: {device['name']}, Channels: {device['max_input_channels']}")


class AudioRecorder(pipeline.Stage):
    """
    Records audio from a real-world recorder via sounddevice
    """
    def __init__(self,
                 device_id: int,
                 samplerate,
                 channels,
                 blocksize,
                 channel_map=None,  # should be a numpy array if wanted
                 destinations=None):
        """
        Initialize the audio recorder
        :param device_id: The device ID. Can be found by calling print_audio_devices()
        :param samplerate: The samplerate of the recorder
        :param channels: The number of channels of the recorde
        :param blocksize: The number of samples per block of audio
        :param channel_map: Reorganizes the recording matrix. For example [2, 3, 4] will put channels [2, 3, 4] into
            recording matrix in rows [0, 1, 2]
        :param destinations: Where the recorder with push data. Should be a class which inherits Stage
        """
        super().__init__(0, 0, destinations, has_process=False)

        self.channel_map = channel_map
        self.device_id = device_id
        self.samplerate = samplerate
        self.channels = channels
        self.blocksize = blocksize
        self.stream = None

    def _audio_callback(self, indata, frames, time, status):
        """
        Called by sounddevice. Called for every block of audio data
        :param indata: Data from the recorder
        :param frames: Data to output devices. Not used
        :param time: Time of the recorder. Not used
        :param status: Error status of the recorder. If error, print it
        :return: None
        """
        if status:
            print(status)
        data = np.array(indata)
        if self.channel_map is not None:
            data = data[:, self.channel_map]
        self.destination_queue_put(data)

    def start(self):
        """
        Starts the recording stream. Must be called by a script at least once
        :return: None
        """
        self.stream = sd.InputStream(
            device=self.device_id,
            channels=self.channels,
            samplerate=self.samplerate,
            blocksize=self.blocksize,
            callback=self._audio_callback
        )
        self.stream.start()

    def stop(self):
        """
        Stops the recording stream
        :return:
        """
        if self.stream:
            self.stream.stop()
            self.stream.close()
