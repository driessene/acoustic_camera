from AccCam.__config__ import __USE_CUPY__

if __USE_CUPY__:
    import cupy as np
else:
    import numpy as np

import logging
import sounddevice as sd
import AccCam.realtime_dsp.pipeline as pipe


# Logging
logger = logging.getLogger(__name__)


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


class AudioRecorder(pipe.Stage):
    """
    Records audio from a real-world recorder via sounddevice
    """
    def __init__(self,
                 device_id: int,
                 samplerate,
                 num_channels,
                 blocksize,
                 channel_map=None,  # should be a numpy array if wanted
                 destinations=None):
        """
        :param device_id: The device ID. Can be found by calling print_audio_devices()
        :param samplerate: The samplerate of the recorder
        :param num_channels: The number of channels of the recorde
        :param blocksize: The number of samples per block of audio
        :param channel_map: Reorganizes the recording matrix. For example [2, 3, 4] will put channels [2, 3, 4] into
            recording matrix in rows [0, 1, 2]
        :param destinations: Where the recorder with push data. Should be a class which inherits Stage
        """
        super().__init__(0, 0, destinations, has_process=False)

        self.channel_map = channel_map
        self.device_id = device_id
        self.samplerate = samplerate
        self.num_channels = num_channels
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
        self.port_put(pipe.Message(data))

    def start(self):
        """
        Starts the recording stream. Must be called by a script at least once
        :return: None
        """
        self.stream = sd.InputStream(
            device=self.device_id,
            channels=self.num_channels,
            samplerate=self.samplerate,
            blocksize=self.blocksize,
            callback=self._audio_callback
        )
        self.stream.start()

        logger.info(f'Stream started on {self.device_id} with {self.num_channels} at {self.samplerate} Hz.'
                    f'Blocksize is {self.blocksize}')

    def stop(self):
        """
        Stops the recording stream
        :return: None
        """
        if self.stream:
            self.stream.stop()
            self.stream.close()

        logger.info(f'Stream {self.device_id} stopped')
