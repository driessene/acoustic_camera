import pyqtgraph as pg
import matplotlib.cm as cm
from Management import pipeline
import numpy as np
import scipy.fft as fft
from PyQt5 import QtCore, QtWidgets, QtGui


class FFTApplication(QtWidgets.QMainWindow, pipeline.Stage):
    """
    A pre-made plotter to plot amplitude and phase of a fft.
    """
    def __init__(self, samplerate, blocksize, channels, freq_range=None, max_pwr=10e7, interval=0, port_size=4):
        QtWidgets.QMainWindow.__init__(self)
        pipeline.Stage.__init__(self, 1, port_size, None, has_process=False)

        # Properties
        self.samplerate = samplerate
        self.blocksize = blocksize
        self.channels = channels
        self.max_pwr = max_pwr

        # Window
        self.setWindowTitle('FFT')
        self.layout = QtWidgets.QGridLayout()
        self.palette = QtGui.QPalette()
        self.setAutoFillBackground(True)

        # Widget
        self.widget = QtWidgets.QWidget()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        # X-data
        self.delta_f = self.samplerate / self.blocksize
        self.x_data = np.arange(-0.5 * self.delta_f * self.blocksize, 0.5 * self.delta_f * self.blocksize, self.delta_f)

        # Plots
        self.pwr_plot_graph = pg.PlotWidget()
        self.layout.addWidget(self.pwr_plot_graph, 0, 0)
        self.pwr_plot_graph.setBackground('black')
        self.pwr_plot_graph.setTitle('Power', color='white', size='18pt')
        self.pwr_plot_graph.setLabel('left', 'Power', color='white', size='20pt')
        self.pwr_plot_graph.setLabel('bottom', 'Hz', color='white', size='20pt')
        self.pwr_plot_graph.showGrid(x=True, y=True)
        self.pwr_plot_graph.setYRange(0, self.max_pwr)
        if freq_range is not None:
            self.pwr_plot_graph.setXRange(*freq_range)

        self.ph_plot_graph = pg.PlotWidget()
        self.layout.addWidget(self.ph_plot_graph, 1, 0)
        self.ph_plot_graph.setBackground('black')
        self.ph_plot_graph.setTitle('Phase', color='white', size='18pt')
        self.ph_plot_graph.setLabel('left', 'Phase', color='white', size='20pt')
        self.ph_plot_graph.setLabel('bottom', 'Hz', color='white', size='20pt')
        self.ph_plot_graph.showGrid(x=True, y=True)
        self.ph_plot_graph.setYRange(-180, 180)
        if freq_range is not None:
            self.ph_plot_graph.setXRange(*freq_range)

        # Lines
        colors = ('white', 'red', 'green', 'blue', 'darkRed', 'darkGreen', 'darkBlue', 'cyan', 'magenta', 'yellow',
                  'grey', 'darkCyan', 'darkMagenta', 'darkYellow', 'darkGrey')

        self.pwr_lines = [self.pwr_plot_graph.plot(
            name='Data',
            pen=pg.mkPen(color=colors[i], width=2),
        ) for i in range(channels)]

        self.ph_lines = [self.ph_plot_graph.plot(
            name='Data',
            pen=pg.mkPen(color=colors[i], width=2),
        ) for i in range(channels)]

        # Make a timer to update plot
        self.interval = interval
        self.timer = QtCore.QTimer()
        self.timer.setInterval(self.interval)
        self.timer.timeout.connect(self._on_frame_update)
        self.timer.start()

    def _on_frame_update(self):
        # Get data, then get power and phase
        data = self.port_get()[0]
        data = fft.fftshift(data)
        pwr_data = np.abs(data) ** 2
        ph_data = np.angle(data, deg=True)

        # Update lines
        for i, (pwr_line, ph_line) in enumerate(zip(self.pwr_lines, self.ph_lines)):
            pwr_line.setData(self.x_data, pwr_data[:, i])
            ph_line.setData(self.x_data, ph_data[:, i])


class ThreeAxisApplication(QtWidgets.QMainWindow, pipeline.Stage):
    """
    A pre-made plotter to plot three axes of data in three different stages. Plots source, after filtering, and doa of
    three axes
    """
    def __init__(self,
                 blocksize: int,
                 num_music_angles: int,
                 x_num_channels: int,
                 y_num_channels: int,
                 z_num_channels: int,
                 interval=0,
                 port_size=4
                 ):
        """
        Initializes the ploter
        :param blocksize: The blocksize of audio data
        :param num_music_angles: The number of music test angles
        :param x_num_channels: The number of channels on the x-axis
        :param y_num_channels: The number of channels on the y-axis
        :param z_num_channels: The number of channels in the z-axis
        :param interval: The time between frame updates in milliseconds
        :param port_size: The size of the input queue. Note that there are nine input queues
        """
        QtWidgets.QMainWindow.__init__(self)
        pipeline.Stage.__init__(self, 9, port_size, None, has_process=False)

        # Mapping of input queues and plots. Queses are linked to the corresponding plot

        # ------------------------------------------------------|--------------------------|
        # |                          |                          |                          |
        # | Plot 0 : x music         | Plot 1 : y music         | Plot 2 : z music         |
        # |                          |                          |                          |
        # |-----------------------------------------------------|--------------------------|
        # |                          |                          |                          |
        # | Plot 3 : x after filter  | Plot 4 : y after filter  | Plot 5 : z after filter  |
        # |                          |                          |                          |
        # |-----------------------------------------------------|--------------------------|
        # |                          |                          |                          |
        # | Plot 6 : x before filter | Plot 7 : y before filter | Plot 8 : z before filter |
        # |                          |                          |                          |
        # |-----------------------------------------------------|--------------------------|

        # Properties
        self.blocksize = blocksize
        self.num_music_angles = num_music_angles
        self.x_num_channels = x_num_channels
        self.y_num_channels = y_num_channels
        self.z_num_channels = z_num_channels

        # Window
        self.setWindowTitle('ThreeAxisApplication')
        self.layout = QtWidgets.QGridLayout()
        self.palette = QtGui.QPalette()
        self.setAutoFillBackground(True)

        # Plots
        self.plots = [pg.PlotWidget() for _ in range(9)]  # a 3x3 matrix of plots
        for i, plot in enumerate(self.plots):
            self.layout.addWidget(plot, i // 3, i % 3)

        # Plot Data
        self.lines = []
        self.y_data = []
        self.x_data = []

        # Line colors
        colormapper = cm.get_cmap('tab10')  # Choose a colormap
        num_colors = max(self.x_num_channels, self.y_num_channels, self.z_num_channels)
        self.colors = [np.multiply(colormapper(i / num_colors)[0:3], 255) for i in range(num_colors)]

        # Widget
        self.widget = QtWidgets.QWidget()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        def init_plot(plot, title, x_label, y_label, x_range, y_range, num_lines, num_points):
            """
            Initializes a plot on the window
            :param plot: The plot to initizlize
            :param title: The title of the plot
            :param x_label: The x label of the plot
            :param y_label: The y label for the plot
            :param x_range: The x range of the plot
            :param y_range: The y range for the plot
            :param num_lines: The number of lines on the plot
            :param num_points: The number of points on the plot
            :return: None
            """
            plot.setBackground('white')
            plot.setTitle(title)
            plot.setLabel('left', y_label)
            plot.setLabel('bottom', x_label)
            plot.setXRange(*x_range)
            plot.setYRange(*y_range)
            # plot.addLegend()

            self.x_data.append(np.linspace(*x_range, num_points))

            if num_lines == 1:
                self.y_data.append(np.zeros(num_points))
            else:
                self.y_data.append(np.zeros((num_points, num_points)))

            x_data = self.x_data[len(self.x_data) - 1]
            y_data = self.y_data[len(self.y_data) - 1]

            if y_data.ndim == 1:
                self.lines.append(plot.plot(
                    x_data,
                    y_data,
                    name='Data',
                    pen=pg.mkPen(color=self.colors[0], width=2),
                ))
            elif y_data.ndim == 2:
                self.lines.append([plot.plot(
                    x_data,
                    y_data[i],
                    name='Data',
                    pen=pg.mkPen(color=self.colors[i], width=2),
                ) for i in range(num_lines)])
            else:
                raise ValueError('data can only be 1D or 2D')

        # Plot 0 - x music
        init_plot(plot=self.plots[0],
                  title='X MUSIC',
                  x_label='Angle (Deg)',
                  y_label='MUSIC',
                  x_range=(-90, 90),
                  y_range=(0, 1),
                  num_lines=1,
                  num_points=self.num_music_angles)
        # Plot 1 - y music
        init_plot(plot=self.plots[1],
                  title='Y MUSIC',
                  x_label='Angle (Deg)',
                  y_label='MUSIC',
                  x_range=(-90, 90),
                  y_range=(0, 1),
                  num_lines=1,
                  num_points=self.num_music_angles)

        # Plot 2 - z music
        init_plot(plot=self.plots[2],
                  title='Z MUSIC',
                  x_label='Angle (Deg)',
                  y_label='MUSIC',
                  x_range=(-90, 90),
                  y_range=(0, 1),
                  num_lines=1,
                  num_points=self.num_music_angles)

        # Plot 3 - x filter
        init_plot(plot=self.plots[3],
                  title='X After Filters',
                  x_label='Sample',
                  y_label='Amplitude',
                  x_range=(0, self.blocksize),
                  y_range=(-1, 1),
                  num_lines=self.x_num_channels,
                  num_points=self.blocksize)
        # Plot 4 - y filter
        init_plot(plot=self.plots[4],
                  title='Y After Filters',
                  x_label='Sample',
                  y_label='Amplitude',
                  x_range=(0, self.blocksize),
                  y_range=(-1, 1),
                  num_lines=self.y_num_channels,
                  num_points=self.blocksize)
        # Plot 5 - z filter
        init_plot(plot=self.plots[5],
                  title='Z After Filters',
                  x_label='Sample',
                  y_label='Amplitude',
                  x_range=(0, self.blocksize),
                  y_range=(-1, 1),
                  num_lines=self.z_num_channels,
                  num_points=self.blocksize)
        # Plot 6 - x source
        init_plot(plot=self.plots[6],
                  title='X Before Filters',
                  x_label='Sample',
                  y_label='Amplitude',
                  x_range=(0, self.blocksize),
                  y_range=(-1, 1),
                  num_lines=self.x_num_channels,
                  num_points=self.blocksize)
        # Plot 7 - y source
        init_plot(plot=self.plots[7],
                  title='Y Before Filters',
                  x_label='Sample',
                  y_label='Amplitude',
                  x_range=(0, self.blocksize),
                  y_range=(-1, 1),
                  num_lines=self.y_num_channels,
                  num_points=self.blocksize)

        # Plot 8 - z source
        init_plot(plot=self.plots[8],
                  title='Z Before Filters',
                  x_label='Sample',
                  y_label='Amplitude',
                  x_range=(0, self.blocksize),
                  y_range=(-1, 1),
                  num_lines=self.z_num_channels,
                  num_points=blocksize)

        # Make a timer to update plot
        self.interval = interval
        self.timer = QtCore.QTimer()
        self.timer.setInterval(self.interval)
        self.timer.timeout.connect(self._on_frame_update)
        self.timer.start()

    def _on_frame_update(self):
        """
        Updates the window. Called every timer timeout
        :return: None
        """
        data_set = self.port_get()  # 9 numpy arrays

        # Per plot in window...
        for i, (plot_data, plot, lines, x_data) in enumerate(zip(data_set, self.plots, self.lines, self.x_data)):
            plot_data = plot_data
            self.y_data[i] = plot_data

            # if several lines
            if plot_data.ndim == 2:
                for j, line in enumerate(lines):
                    line.setData(x_data, self.y_data[i][:, j].real)

            # if one line
            elif plot_data.ndim == 1:
                lines.setData(self.x_data[i], self.y_data[i].real)
            else:
                raise Exception('data can only be 1D or 2D')
