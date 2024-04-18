from Management import Stage, Message
from datetime import datetime
import pandas as pd
import logging

# logging
logger = logging.getLogger(__name__)


class MatrixToCSV(Stage):
    """
    Save a matrix to a csv file. It is recommended to use Management.Accumulator before this stage to get data
    """
    def __init__(self, label: str, path: str, port_size=4, destinations=None):
        """
        :param label: Label of the file. For example, if label is RECORDING, the file will save as:
            RECORDING-04-18-2024-16-41-18.89 if the data is 4/18/2024 at 16:41:18.89
        :param path: Path the put the file in. Must be a folder with no / or \ at the end of the string
        :param port_size:
        :param destinations:
        """
        super().__init__(1, port_size, destinations)
        self.label = label
        self.path = path

    def run(self):
        data = self.port_get()[0]
        df = pd.DataFrame(data)
        path = f'{self.path}/{self.label}_{datetime.now().strftime("%y-%m-%d-%H-%M-%S.%f")}'
        df.to_csv(path)
        logger.info(f'data with shape of {data.shape} saved to {path}')


class CSVToPipeline(Stage):
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
        self.dataframe = pd.read_csv(path).to_numpy()
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
            self.port_put(Message(block, index=self._i))
            self._i += 1
        except IndexError:
            logger.warning(f'Data source from path {self.path} depleted')
            self.stop()

    def start(self):
        super().start()

        # Reset initial conditions
        self._i = 0