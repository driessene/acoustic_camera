from AccCam.__config__ import __USE_CUPY__

if __USE_CUPY__:
    import cupy as np
else:
    import numpy as np

import AccCam.realtime_dsp.pipeline as control
from datetime import datetime
import logging

# logging
logger = logging.getLogger(__name__)


class ToDisk(control.Stage):
    """
    Save a matrix to a csv file. It is recommended to use Management. Accumulator before this stage to get data.
    Can also continue pushing data if asked.
    """
    def __init__(self, label: str, path: str, port_size=4, destinations=None):
        """
        :param label: Label of the file. For example, if label is RECORDING, the file will save as:
            RECORDING-04-18-2024-16-41-18.89 if the data is 4/18/2024 at 16:41:18.89
        :param path: Path the put the file in. Must be a folder with no / at the end of the string
        """
        super().__init__(1, port_size, destinations)
        self.label = label
        self.path = path

    def run(self):
        data = self.port_get()[0].payload
        path = f'{self.path}/{self.label}_{datetime.now().strftime("%d-%m-%y-%H-%M-%S.%f")}.npy'
        np.save(path, data)
        logger.info(f'data with shape of {data.shape} saved to {path}')
        self.port_put(data)


class FromDisk(control.Stage):
    """
    Take a CSV, break it into blocks, and push into pipeline. Breaking it down allows for batch processing.
    Use an accumulator if you wouldn't like to break it down at the end of the pipeline.
    """
    def __init__(self, path: str, blocksize: int, axis: int, destinations):
        """
        :param path: The path of the source file
        :param blocksize: The number of rows / columns to grab and push at once
        :param axis: The axis which to iterate over
        """
        super().__init__(0, 0, destinations)
        self.path = path
        self.blocksize = blocksize
        self.axis = axis
        self.dataframe = np.load(path)
        self._i = 0

    def run(self):
        try:
            if self.axis == 0:
                block = self.dataframe[:, self._i * self.blocksize:self._i * self.blocksize + self.blocksize]
            elif self.axis == 1:
                block = self.dataframe[self._i * self.blocksize:self._i * self.blocksize + self.blocksize, :]
            else:
                logger.warning(f'axis = {self.axis} is not valid, defaulting to axis 0.')
                block = self.dataframe[:, self._i * self.blocksize:self._i * self.blocksize + self.blocksize]
            self.port_put(control.Message(block, index=self._i))
            self._i += 1
        except IndexError:
            logger.warning(f'Data source from path {self.path} depleted')
            self.stop()

    def start(self):
        super().start()

        # Reset initial conditions
        self._i = 0
