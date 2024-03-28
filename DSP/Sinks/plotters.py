import pyqtgraph as pg
import matplotlib.cm as cm
from Management import pipeline
import numpy as np
from PyQt5 import QtCore, QtWidgets, QtGui


class SingleLinePlotter(QtWidgets.QMainWindow, pipeline.Stage):
    """
    A real-time plotter. Plots a single line
    """
    def __init__(self,
                 title: str,
                 x_label: str,
                 y_label: str,
                 x_range: tuple,
                 y_range: tuple,
                 blocksize: int,
                 x_data=None,
                 interval: int = 0,
                 queue_size: int = 4
                 ):
        """
        Initializes a single line plotter
        :param title: The title of the plotter
        :param x_label: The x-label of the plotter
        :param y_label: The y-label for the plotter
        :param x_range: The x-range of the plotter (for visuals only)
        :param y_range: The y-range for the plotter (for visuals only)
        :param blocksize: The number of points per line on the plot
        :param x_data: Optional. Provide X-axis data. If not given, assume to be 0 to blocksize
        :param interval: The time between frame updates in milliseconds. Defaults to 0 such that the plot waits for data
        :param queue_size: Size of the input queue
        """
        QtWidgets.QMainWindow.__init__(self)
        pipeline.Stage.__init__(self, 1, queue_size, None, has_process=False)

        # Styling
        self.plot_graph = pg.PlotWidget()
        self.setCentralWidget(self.plot_graph)
        self.plot_graph.setBackground('black')
        self.plot_graph.setTitle(title, color='white', size='18pt')
        self.plot_graph.setLabel('left', y_label, color='white', size='20pt')
        self.plot_graph.setLabel('bottom', x_label, color='white', size='20pt')
        self.plot_graph.showGrid(x=True, y=True)
        self.plot_graph.setMouseEnabled(y=False)
        self.plot_graph.setMouseEnabled(x=False)
        self.x_range = x_range
        self.y_range = y_range
        self.blocksize = blocksize

        if x_data is None:
            self.x_data = np.arange(self.blocksize)
        else:
            self.x_data = x_data

        # self.plot_graph.setXRange(x_range[0], x_range[1])
        # self.plot_graph.setYRange(y_range[0], y_range[1])

        # Data
        self.line_data = np.zeros((2, 2))
        self.line = self.plot_graph.plot(
            self.line_data[0],
            self.line_data[1],
            name='Data',
            pen=pg.mkPen(color='white', width=2)
        )

        # Make a timer to update plot
        self.interval = interval
        self.timer = QtCore.QTimer()
        self.timer.setInterval(self.interval)
        self.timer.timeout.connect(self._on_frame_update)
        self.timer.start()

    def _on_frame_update(self):
        """
        Called every frame update. Called by the timer
        :return: None
        """
        data = self.input_queue_get()[0]
        self.line_data = (self.x_data, data)
        self.line.setData(*self.line_data)

class SingleLinePlotterParametric(SingleLinePlotter):
    """
    A single line plotter when both X and Y data are both provided. Data in input queue must be a tuple (X, Y)
    """
    def __init__(self,
                 title: str,
                 x_label: str,
                 y_label: str,
                 x_range: tuple,
                 y_range: tuple,
                 blocksize: int,
                 interval: int = 0,
                 queue_size: int = 4
                 ):
        super().__init__(title, x_label, y_label, x_range, y_range, blocksize, None, interval, queue_size)

    def _on_frame_update(self):
        """
        Called every frame update. Called by the timer
        :return: None
        """
        data = self.input_queue_get()[0]
        self.line_data = (data[0], data[1])
        self.line.setData(*self.line_data)

class MultiLinePlotter(QtWidgets.QMainWindow, pipeline.Stage):
    """
    A real-time plotter. Plots multiple lines on a single plot
    """
    def __init__(self,
                 title: str,
                 x_label: str,
                 y_label: str,
                 x_range: tuple,
                 y_range: tuple,
                 num_lines: int,
                 blocksize: int,
                 x_data=None,
                 interval: int = 0,
                 queue_size: int = 4
                 ):
        """
        Initializes the plotter
        :param title: Title of the plot
        :param x_label: The x-label of the plot
        :param y_label: The y-label for the plot
        :param x_range: The x-range of the plot
        :param y_range: The y-range of the plot
        :param num_lines: The number of lines to plot
        :param blocksize: The number of points per line on the plot
        :param x_data: Optional. X-axis data. If not given, assume to be 0 to blocksize
        :param interval: The time between frame updates in milliseconds
        :param queue_size: Size of the input queue
        """
        QtWidgets.QMainWindow.__init__(self)
        pipeline.Stage.__init__(self, 1, queue_size, None, has_process=False)

        # Styling
        self.plot_graph = pg.PlotWidget()
        self.setCentralWidget(self.plot_graph)
        self.plot_graph.setBackground('black')
        self.plot_graph.setTitle(title, color='white', size='18pt')
        self.plot_graph.setLabel('left', y_label, color='white', size='20pt')
        self.plot_graph.setLabel('bottom', x_label, color='white', size='20pt')
        self.plot_graph.showGrid(x=True, y=True)
        self.plot_graph.setMouseEnabled(y=False)
        self.plot_graph.setMouseEnabled(x=False)
        self.x_range = x_range
        self.y_range = y_range
        self.blocksize = blocksize
        self.plot_graph.setXRange(x_range[0], x_range[1])
        self.plot_graph.setYRange(y_range[0], y_range[1])

        if x_data is None:
            self.x_data = np.arange(self.blocksize)
        else:
            self.x_data = x_data

        # Data
        self.line_data = np.zeros((2, blocksize, num_lines))
        colors = ('white', 'red', 'green', 'blue', 'darkRed', 'darkGreen', 'darkBlue', 'cyan', 'magenta', 'yellow',
                  'grey', 'darkCyan', 'darkMagenta', 'darkYellow', 'darkGrey')
        self.lines = [self.plot_graph.plot(
            self.line_data[0, :, i],
            self.line_data[1, :, i],
            name='Data',
            pen=pg.mkPen(color=colors[i], width=2),
        ) for i in range(num_lines)]

        # Make a timer to update plot
        self.interval = interval
        self.timer = QtCore.QTimer()
        self.timer.setInterval(self.interval)
        self.timer.timeout.connect(self._on_frame_update)
        self.timer.start()

    def _on_frame_update(self):
        """
        Called every frame update. Called by the timer
        :return: None
        """
        data_set = self.input_queue_get()[0]
        for i, (data, line) in enumerate(zip(data_set.T, self.lines)):
            self.line_data[0, :, i] = self.x_data
            self.line_data[1, :, i] = data.real
            line.setData(*self.line_data[:, :, i])


class MultiLinePlotterParametric(MultiLinePlotter):
    """
    A multiple line plotter when both X and Y data are both provided. Data in input queue must be a tuple (X, Y)
    """
    def __init__(self,
                 title: str,
                 x_label: str,
                 y_label: str,
                 x_range: tuple,
                 y_range: tuple,
                 num_lines: int,
                 blocksize: int,
                 interval: int = 0,
                 queue_size: int = 4
                 ):
        super().__init__(title, x_label, y_label, x_range, y_range, num_lines,
                         blocksize, None, interval, queue_size)

    def _on_frame_update(self):
        """
        Called every frame update. Called by the timer
        :return: None
        """
        x_data, y_data = self.input_queue_get()[0]
        x_data, y_data = x_data.T.real, y_data.T.real
        for i, (x, y, line) in enumerate(zip(x_data, y_data, self.lines)):
            self.line_data[0, :, i] = x
            self.line_data[1, :, i] = y
            line.setData(*self.line_data[:, :, i])


class FFTApplication(QtWidgets.QMainWindow, pipeline.Stage):
    """
    A pre-made plotter to plot amplitude and phase of a fft.
    """
    def __init__(self, samplerate, channels, interval=0, queue_size=4):
        QtWidgets.QMainWindow.__init__(self)
        pipeline.Stage.__init__(self, 1, queue_size, None, has_process=False)

        # Properties
        self.samplerate = samplerate
        self.N = int(samplerate // 2)
        self.channels = channels

        # Window
        self.setWindowTitle('FFT')
        self.layout = QtWidgets.QGridLayout()
        self.palette = QtGui.QPalette()
        self.setAutoFillBackground(True)

        # Plots
        self.abs_plot_graph = pg.PlotWidget()
        self.layout.addWidget(self.abs_plot_graph, 0, 0)
        self.abs_plot_graph.setBackground('black')
        self.abs_plot_graph.setTitle('Magnitude', color='white', size='18pt')
        self.abs_plot_graph.setLabel('left', 'Magnitude', color='white', size='20pt')
        self.abs_plot_graph.setLabel('bottom', 'Hz', color='white', size='20pt')
        self.abs_plot_graph.showGrid(x=True, y=True)
        self.abs_plot_graph.setXRange(0, self.samplerate / 2)
        self.abs_plot_graph.setYRange(0, 10)

        self.ang_plot_graph = pg.PlotWidget()
        self.layout.addWidget(self.ang_plot_graph, 0, 1)
        self.ang_plot_graph.setBackground('black')
        self.ang_plot_graph.setTitle('Phase', color='white', size='18pt')
        self.ang_plot_graph.setLabel('left', 'Phase', color='white', size='20pt')
        self.ang_plot_graph.setLabel('bottom', 'Hz', color='white', size='20pt')
        self.ang_plot_graph.showGrid(x=True, y=True)
        self.ang_plot_graph.setXRange(0, self.samplerate / 2)
        self.ang_plot_graph.setYRange(-np.pi, np.pi)

        # Lines
        colors = ('white', 'red', 'green', 'blue', 'darkRed', 'darkGreen', 'darkBlue', 'cyan', 'magenta', 'yellow',
                  'grey', 'darkCyan', 'darkMagenta', 'darkYellow', 'darkGrey')

        self.abs_lines_data = np.zeros((self.N, self.channels))
        self.abs_lines = [self.abs_plot_graph.plot(
            np.arange(self.N),
            self.abs_lines_data[:, i],
            name='Data',
            pen=pg.mkPen(color=colors[i], width=2),
        ) for i in range(channels)]

        self.ang_lines_data = np.zeros((self.N, self.channels))
        self.ang_lines = [self.ang_plot_graph.plot(
            np.arange(self.N),
            self.ang_lines_data[:, i],
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
        self.abs_lines_data, self.ang_lines_data = self.input_queue_get()[0]    # (abs, ang)
        for i, (abs_line, ang_line) in enumerate(zip(self.abs_lines, self.ang_lines)):
            print(self.abs_lines_data[:, i].size)
            print(self.abs_lines_data[:, i].ndim)
            print(self.abs_lines_data[:, i])
            abs_line.setData([np.arange(self.abs_lines_data[:, i].size), self.abs_lines_data[:, i]])
            ang_line.setData([np.arange(self.ang_lines_data[:, i].size), self.ang_lines_data[:, i]])


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
                 queue_size=4
                 ):
        """
        Initializes the ploter
        :param blocksize: The blocksize of audio data
        :param num_music_angles: The number of music test angles
        :param x_num_channels: The number of channels on the x-axis
        :param y_num_channels: The number of channels on the y-axis
        :param z_num_channels: The number of channels in the z-axis
        :param interval: The time between frame updates in milliseconds
        :param queue_size: The size of the input queue. Note that there are nine input queues
        """
        QtWidgets.QMainWindow.__init__(self)
        pipeline.Stage.__init__(self, 9, queue_size, None, has_process=False)

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
        data_set = self.input_queue_get()  # 9 cupy arrays

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
