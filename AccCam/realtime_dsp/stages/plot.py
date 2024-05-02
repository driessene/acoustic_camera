import numpy as np
import logging
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import AccCam.direction_of_arrival as doa
import AccCam.realtime_dsp.pipeline as pipe
import AccCam.visual as vis
import cv2 as cv


# logging
logger = logging.getLogger(__name__)


class LinePlotter(pipe.Stage):
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
                 x_data: np.ndarray = None,
                 x_extent: tuple = None,
                 y_extent: tuple = None,
                 port_size=4,
                 destinations=None):
        """
        :param title: The title of the plot
        :param x_label: The x label of the plot
        :param y_label: The y label of the plot
        :param num_points: The number of data points per line
        :param num_lines: The number of lines to plot
        :param interval: The time delay in seconds between each frame update
        :param legend: If ture, show a legend for each line
        :param x_data: If provided, set the x component for each line to this
        :param x_extent: If provided, set the visual range of the plot on the x-axis to this
        :param y_extent: If provided, set the visual range of the plot on the y-axis to this
        :param port_size: The size of the input port
        """
        super().__init__(1, port_size, destinations, False)

        # Properties
        self.num_points = num_points
        self.num_lines = num_lines

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
        message = self.port_get()[0]
        data = message.payload

        # Data checking
        if data.shape != (self.num_points, self.num_lines) and data.shape != (self.num_points,):
            logger.warning(f'Data shape of {data.shape} does not match expected shape of '
                           f'{(self.num_points, self.num_lines)}')

        # If a signal matrix, transpose
        if data.ndim > 1:
            data = data.T

        # Plot
        for (y, plot) in zip(data, self.plots):
            plot.set_ydata(y)

    @staticmethod
    def show():
        plt.show()


class PolarPlotter(pipe.Stage):
    """
    Take a vector (1d numpy array) and plot it on a pollar plot. Same as LinePlotter, but plots r, theta rather
    than x, y
    """
    def __init__(self,
                 title: str,
                 num_points: int,
                 num_lines: int,
                 interval: float,
                 legend: bool = False,
                 theta_data: np.ndarray = None,
                 theta_extent: tuple = None,
                 radius_extent: tuple = None,
                 port_size=4,
                 destinations=None
                 ):
        """
        :param title: The title of the plot
        :param num_points: The number of data points per line
        :param num_lines: The number of lines to plot
        :param interval: The time delay in seconds between each frame update
        :param legend: If ture, show a legend for each line
        :param theta_data: If provided, set the theta component for each line to this
        """
        super().__init__(1, port_size, destinations, False)

        # Properties
        self.num_points = num_points
        self.num_lines = num_lines

        # Setup ax and fig
        self.fig, self.ax = plt.subplots(subplot_kw={'projection': 'polar'})
        self.ax.set_title(title)

        # Setup theta data for each line
        self.theta = theta_data
        if self.theta is None:
            self.theta = np.arange(num_points)

        # Set ranges if asked
        if theta_extent is not None:
            self.ax.set_xlim(theta_extent)
        if radius_extent is not None:
            self.ax.set_ylim(radius_extent)

        # Initialize each line
        self.plots = [self.ax.plot(self.theta, np.zeros_like(self.theta))[0] for _ in range(num_lines)]

        # Set a legend if asked
        if legend:
            self.ax.legend(self.plots, [f'Channel {i}' for i in range(len(self.plots))], loc='upper right')

        # Setup animation
        self.anim = FuncAnimation(self.fig, self._on_frame_update, interval=interval)

    def _on_frame_update(self, frame):
        message = self.port_get()[0]
        data = message.payload

        # Data checking
        if data.shape != (self.num_points, self.num_lines) and data.shape != (self.num_points,):
            logger.warning(f'Data shape of {data.shape} does not match expected shape of '
                           f'{(self.num_points, self.num_lines)} or {(self.num_points,)}')

        # If a vector:
        if data.ndim == 1:
            if self.num_lines > 1:
                logger.warning(f'Only received 1D data for several lines. Will not plot properly.')
            self.plots[0].set_ydata(data)

        # If a matrix:
        elif data.ndim == 2:
            data = data.T
            for (y, plot) in zip(data, self.plots):
                plot.set_ydata(y)

        else:
            logger.warning(f'Received data of {data.ndim}. Only accepts 1D or 2D data.')

    @staticmethod
    def show():
        plt.show()


class HeatmapPlotter(pipe.Stage):
    """
    Plots a 2d matrix flat on a surface. Data is expected to be 1D, which is from a 2D matrix, but flattened. Use
    np.ravel() if needed to flatten a matrix. For example, a MUSIC output can have 2 axes (inclination, azimuth), but is
    still represented by a 1D vector.
    """
    def __init__(self,
                 title: str,
                 x_label: str,
                 y_label: str,
                 x_data: np.ndarray,
                 y_data: np.ndarray,
                 interval: float,
                 x_extent: tuple = None,
                 y_extent: tuple = None,
                 z_extent: tuple = None,
                 cmap: str = 'viridis',
                 port_size=4,
                 destinations=None):
        """
        :param title: The title of the plot
        :param x_label: The x label of the plot
        :param y_label: The y label of the plot
        :param x_data: The x-axis data of the incoming data. If unknown, set to np.arrange(data.shape[0])
        :param y_data: The y-axis data of the incoming data. If unknown, set to np.arrange(data.shape[1])
        :param interval: The time delay in seconds between each frame update
        :param x_extent: If provided, set the visual range of the plot on the x-axis to this
        :param y_extent: If provided, set the visual range of the plot on the y-axis to this
        :param z_extent: If provided, set the visual range of the plot on the z-axis to this
        :param port_size: The size of the input port
        """
        super().__init__(1, port_size, destinations, False)

        self.xx, self.yy = np.meshgrid(x_data, y_data)
        self.interval = interval

        self.fig, self.ax = plt.subplots()
        self.ax.set_title(title)
        self.ax.set_xlabel(x_label)
        self.ax.set_ylabel(y_label)

        self.cmap = cmap

        if x_extent is not None:
            self.ax.set_xlim(x_extent)
        if y_extent is not None:
            self.ax.set_ylim(y_extent)

        self.z_extent = z_extent
        if self.z_extent is None:
            self.z_extent = (0, 1)

        self.plot = self.ax.pcolormesh(self.xx, self.yy, np.zeros_like(self.xx),
                                       vmin=self.z_extent[0], vmax=self.z_extent[1], cmap=self.cmap)

        self.anim = FuncAnimation(self.fig, self._on_frame_update, interval=self.interval)

    def _on_frame_update(self, frame):
        message = self.port_get()[0]
        data = message.payload

        # Data checking
        if data.size != self.xx.size:
            logger.warning(f'Data shape of {data.shape} does not match expected shape of {self.xx.shape}')

        # Plot
        self.plot.set_array(data)
        return self.plot,

    @staticmethod
    def show():
        plt.show()


class HeatmapPlotterVideo(pipe.Stage):
    """
    A HeatmapPlotter with a video feed displayed behind the heatmap. The spacing of angles of the Estimator must be
    linear for this plotter, unlike HeatmapPlotter.
    """

    def __init__(self,
                 structure: doa.Structure,
                 camera: vis.Camera,
                 title: str,
                 x_label: str,
                 y_label: str,
                 x_len: int,
                 y_len: int,
                 interval: float,
                 cmap = cv.COLORMAP_JET,
                 port_size=4,
                 destinations=None):
        super().__init__(1, port_size, destinations, False)

        self.interval = interval

        self.fig, self.ax = plt.subplots()
        self.ax.set_title(title)
        self.ax.set_xlabel(x_label)
        self.ax.set_ylabel(y_label)

        self.cmap = cmap

        self.plot = self.ax.imshow(np.zeros((x_len, y_len, 3)))

        self.anim = FuncAnimation(self.fig, self._on_frame_update, interval=self.interval)

        # Video
        self.camera = camera

        # Audio
        self.structure = structure

    def _on_frame_update(self, frame):
        # Audio get
        message = self.port_get()[0]
        payload = message.payload
        payload_uint8 = np.uint8(payload * 255)
        raw_audio = payload_uint8.reshape(self.structure.inclination_resolution, self.structure.azimuth_resolution)
        audio = cv.applyColorMap(raw_audio, self.cmap)

        # Image get
        image = self.camera.read()

        # Superimpose
        superimpose = cv.addWeighted(image, 0.5, audio, 0.5, 0)

        # Plot
        self.plot.set_array(superimpose)

    @staticmethod
    def show():
        plt.show()