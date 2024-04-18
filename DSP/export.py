from Management import Stage
from datetime import datetime
import pandas as pd


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
        df.to_csv(f'{self.path}/{self.label}_{datetime.now().strftime("%y-%m-%d-%H-%M-%S.%f")}')
