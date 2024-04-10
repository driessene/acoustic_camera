from .. import config

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from Management.pipeline import Stage


class LinePlotter(Stage):
    """
    Plot a line or several lines on a plot. Data is expected to be 2d, with each 0'th axis being a line
    (1d for one line).
    """
    def __init__(self,
                 title: str,
                 x_label: str,
                 y_label: str,
                 num_points: int,
                 num_lines: int,
                 interval: float,
                 legend: bool = False,
                 x_data: np.array = None,
                 x_extent: list = None,
                 y_extent: list = None,
                 port_size=4):
        """
        :param title: The title of the plot
        :param x_label: The x label of the plot
        :param y_label: The y label of the plot
        :param num_points: The number of data points per line
        :param num_lines: The number of lines to plot
        :param interval: The time delay in seconds beteween each frame update
        :param legend: If ture, show a lagend for each line
        :param x_data: If provided, set the x component for each line to this
        :param x_extent: If provided, set the visual range of the plot on the x-axis to this
        :param y_extent: If provided, set the visual range of the plot on the y-axis to this
        :param port_size: The size of the input port
        """
        super().__init__(1, port_size, None, False)
        # Setup ax and fig
        self.fig, self.ax = plt.subplots()
        self.ax.set_title(title)
        self.ax.set_xlabel(x_label)
        self.ax.set_ylabel(y_label)

        # Setup x data for each line
        self.x = x_data
        if self.x is None:
            self.x = np.arange(num_points)

        # Set ranges if asked
        if x_extent is not None:
            self.ax.set_xlim(x_extent)
        if y_extent is not None:
            self.ax.set_ylim(y_extent)

        # Initialize each line
        self.plots = [self.ax.plot(self.x, np.zeros_like(self.x))[0] for _ in range(num_lines)]

        # Set a legend if asked
        if legend:
            self.ax.legend(self.plots, [f'Channel {i}' for i in range(len(self.plots))], loc='upper right')

        # Setup animation
        self.anim = FuncAnimation(self.fig, self._on_frame_update, interval=interval)

    def _on_frame_update(self, frame):
        data = self.port_get()[0]

        # Unpack if cupy
        if config.USE_CUPY:
            data = data.get()

        # If a signal matrix, transpose
        if data.ndim > 1:
            data = data.T

        for (y, plot) in zip(data, self.plots):
            plot.set_ydata(y)


class ThreeDimPlotter(Stage):
    def __init__(self,
                 title: str,
                 x_label: str,
                 y_label: str,
                 x_data: np.array,
                 y_data: np.array,
                 interval: float,
                 x_extent: float = None,
                 y_extent: float = None,
                 port_size=4):
        """
        :param title: The title of the plot
        :param x_label: The x label of the plot
        :param y_label: The y label of the plot
        :param x_data: The x-axis data of the incoming data. If unknown, set to np.arange(data.shape[0])
        :param y_data: The y-axis data of the incoming data. If unknown, set to np.arange(data.shape[1])
        :param interval: The time delay in seconds between each frame update
        :param x_extent: If provided, set the visual range of the plot on the x-axis to this
        :param y_extent: If provided, set the visual range of the plot on the y-axis to this
        :param port_size: The size of the input port
        """
        super().__init__(1, port_size, None, False)

        self.xx, self.yy = np.meshgrid(x_data, y_data)
        self.interval = interval

        self.fig, self.ax = plt.subplots()
        self.ax.set_title(title)
        self.ax.set_xlabel(x_label)
        self.ax.set_ylabel(y_label)

        if x_extent is not None:
            self.ax.set_xlim(x_extent)
        if y_extent is not None:
            self.ax.set_ylim(y_extent)

        self.plot = self.ax.pcolormesh(self.xx, self.yy, np.random.rand(*self.xx.shape))

        self.anim = FuncAnimation(self.fig, self._on_frame_update, interval=self.interval)

    def _on_frame_update(self, frame):
        data = self.port_get()[0]

        # Unpack if cupy
        if config.USE_CUPY:
            data = data.get()

        self.plot.set_array(data)
        return self.plot,
