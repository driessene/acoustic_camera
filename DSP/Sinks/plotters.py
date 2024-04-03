import pyqtgraph as pg
from Management import pipeline
import numpy as np
from PyQt5 import QtCore, QtWidgets


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
                 port_size=4
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
        """
        QtWidgets.QMainWindow.__init__(self)
        pipeline.Stage.__init__(self, 1, port_size, None, has_process=False)

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
        self.line = self.plot_graph.plot(
            name='Data',
            pen=pg.mkPen(color='white', width=2)
        )

        # Make a timer to update plot
        self.timer = QtCore.QTimer()
        self.timer.setInterval(0)
        self.timer.timeout.connect(self._on_frame_update)
        self.timer.start()

    def _on_frame_update(self):
        """
        Called every frame update. Called by the timer
        :return: None
        """
        self.line.setData(self.port_get()[0])


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
                 ):
        super().__init__(title, x_label, y_label, x_range, y_range, blocksize, None)

    def _on_frame_update(self):
        """
        Called every frame update. Called by the timer
        :return: None
        """
        self.line.setData(*self.port_get()[0])


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
                 port_size=4
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
        """
        QtWidgets.QMainWindow.__init__(self)
        pipeline.Stage.__init__(self, 1, port_size, has_process=False)

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
        colors = ('white', 'red', 'green', 'blue', 'darkRed', 'darkGreen', 'darkBlue', 'cyan', 'magenta', 'yellow',
                  'grey', 'darkCyan', 'darkMagenta', 'darkYellow', 'darkGrey')
        self.lines = [self.plot_graph.plot(
            name='Data',
            pen=pg.mkPen(color=colors[i], width=2),
        ) for i in range(num_lines)]

        # Make a timer to update plot
        self.timer = QtCore.QTimer()
        self.timer.setInterval(0)
        self.timer.timeout.connect(self._on_frame_update)
        self.timer.start()

    def _on_frame_update(self):
        """
        Called every frame update. Called by the timer
        :return: None
        """
        data_set = self.port_get()[0]
        for data, line in zip(data_set.T, self.lines):
            line.setData(*data)


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
                 port_size: int = 4
                 ):
        super().__init__(title, x_label, y_label, x_range, y_range, num_lines,
                         blocksize, None, port_size)

    def _on_frame_update(self):
        """
        Called every frame update. Called by the timer
        :return: None
        """
        x_data, y_data = self.port_get()[0]
        x_data, y_data = x_data.T.real, y_data.T.real
        for x, y, line in zip(x_data, y_data, self.lines):
            line.setData(x, y)
