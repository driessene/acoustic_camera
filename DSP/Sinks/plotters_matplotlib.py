import matplotlib.pyplot as plt
import matplotlib.animation as ani
from Management.pipeline import Stage
import numpy as np


class ThreeDimPlot(Stage):
    def __init__(self,
                 title: str,
                 x_label: str,
                 y_label: str,
                 x_data: np.array,
                 y_data: np.array,
                 x_extent: tuple = None,
                 y_extent: tuple = None,
                 port_size=4):
        super().__init__(1, port_size, None, True)
        self.title = title
        self.x_label, self.y_label = x_label, y_label
        self.x_extent, self.y_extent = x_extent, y_extent
        self.x_data, self.y_data = np.meshgrid(x_data, y_data)

        self.fig, self.ax = plt.subplots()
        self.plot = self.ax.contour(self.x_data, self.y_data, np.zeros_like(self.x_data))

    def run(self):
        data = self.port_get()[0]
        data = np.reshape(data, self.x_data.shape)

        self.ax.clear()
        self.ax.set_title(self.title)
        self.ax.set_xlabel(self.x_label)
        self.ax.set_ylabel(self.y_label)

        self.ax.contour(self.x_data, self.y_data, data)
        plt.pause(0.1)
