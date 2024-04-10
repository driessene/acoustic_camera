import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QTimer
from Management import pipeline
import numpy as np

from time import perf_counter


class SingleLinePlotter(QMainWindow, pipeline.Stage):
    """
    A real-time plotter. Plots a single line
    """
    def __init__(self,
                 title: str,
                 x_label: str,
                 y_label: str,
                 x_extent: tuple | None,
                 y_extent: tuple | None,
                 blocksize: int,
                 x_data=None,
                 port_size=4
                 ):
        """
        Initializes a single line plotter
        :param title: The title of the plotter
        :param x_label: The x-label of the plotter
        :param y_label: The y-label for the plotter
        :param x_extent: The visual x-range of the plotter
        :param y_extent: The visual y-range for the plotter
        :param blocksize: The number of points per line on the plot
        :param x_data: Optional. Provide X-axis data. If not given, assume to be 0 to blocksize. Use to set X_range
            if wanted.
        """
        QMainWindow.__init__(self)
        pipeline.Stage.__init__(self, 1, port_size, None, has_process=False)

        # Styling
        self.plot_graph = pg.PlotWidget()
        self.setCentralWidget(self.plot_graph)
        self.plot_graph.setBackground('black')
        self.plot_graph.setTitle(title, color='white', size='18pt')
        self.plot_graph.setLabel('left', y_label, color='white', size='20pt')
        self.plot_graph.setLabel('bottom', x_label, color='white', size='20pt')
        self.plot_graph.showGrid(x=True, y=True)
        self.x_extent = x_extent
        self.y_extent = y_extent

        self.x_data = x_data
        if self.x_data is None:
            self.x_data = np.arange(self.blocksize)

        if self.x_range is not None:
            self.plot_graph.setXRange(*x_extent)
        if self.y_range is not None:
            self.plot_graph.setYRange(*y_extent)

        # Data
        self.line = self.plot_graph.plot(
            name='Data',
            pen=pg.mkPen(color='white', width=2)
        )

        # Make a timer to update plot
        self.timer = QTimer()
        self.timer.setInterval(0)
        self.timer.timeout.connect(self._on_frame_update)
        self.timer.start()

    def _on_frame_update(self):
        """
        Called every frame update. Called by the timer
        :return: None
        """
        self.line.setData(self.x_data, self.port_get()[0])


class SingleLinePlotterParametric(SingleLinePlotter):
    """
    A single line plotter when both X and Y data are both provided. Data in input queue must be a tuple (X, Y)
    """
    def __init__(self,
                 title: str,
                 x_label: str,
                 y_label: str,
                 x_extent: tuple | None,
                 y_extent: tuple | None,
                 blocksize: int,
                 x_data
                 ):
        super().__init__(title, x_label, y_label, x_extent, y_extent, blocksize, x_data)

    def _on_frame_update(self):
        """
        Called every frame update. Called by the timer
        :return: None
        """
        self.line.setData(*self.port_get()[0])


class MultiLinePlotter(QMainWindow, pipeline.Stage):
    """
    A real-time plotter. Plots multiple lines on a single plot
    """
    def __init__(self,
                 title: str,
                 x_label: str,
                 y_label: str,
                 x_extent: tuple,
                 y_extent: tuple,
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
        :param x_extent: The visual x-range of the plot
        :param y_extent: The visual y-range of the plot
        :param num_lines: The number of lines to plot
        :param blocksize: The number of points per line on the plot
        :param x_data: Optional. X-axis data. If not given, assume to be 0 to blocksize
        """
        QMainWindow.__init__(self)
        pipeline.Stage.__init__(self, 1, port_size, has_process=False)

        # Styling
        self.plot_graph = pg.PlotWidget()
        self.setCentralWidget(self.plot_graph)
        self.plot_graph.setBackground('black')
        self.plot_graph.setTitle(title, color='white', size='18pt')
        self.plot_graph.setLabel('left', y_label, color='white', size='20pt')
        self.plot_graph.setLabel('bottom', x_label, color='white', size='20pt')
        self.plot_graph.showGrid(x=True, y=True)
        self.blocksize = blocksize

        # Range
        self.x_extent = x_extent
        self.y_extent = y_extent
        if self.x_extent is not None:
            self.plot_graph.setXRange(*self.x_extent)
        if self.y_extent is not None:
            self.plot_graph.setYRange(*self.y_extent)

        # X data
        self.x_data = x_data
        if self.x_data is None:
            self.x_data = np.arange(self.blocksize)

        # Data
        colors = ('white', 'red', 'green', 'blue', 'darkRed', 'darkGreen', 'darkBlue', 'cyan', 'magenta', 'yellow',
                  'grey', 'darkCyan', 'darkMagenta', 'darkYellow', 'darkGrey')
        self.lines = [self.plot_graph.plot(
            name='Data',
            pen=pg.mkPen(color=colors[i], width=2),
        ) for i in range(num_lines)]

        # Make a timer to update plot
        self.timer = QTimer()
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
            line.setData(data)


class MultiLinePlotterParametric(MultiLinePlotter):
    """
    A multiple line plotter when both X and Y data are both provided. Data in input queue must be a tuple (X, Y)
    """
    def __init__(self,
                 title: str,
                 x_label: str,
                 y_label: str,
                 x_extent: tuple,
                 y_extent: tuple,
                 num_lines: int,
                 blocksize: int,
                 port_size: int = 4
                 ):
        super().__init__(title, x_label, y_label, x_extent, y_extent, num_lines,
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


class ThreeDimPlotter(QMainWindow, pipeline.Stage):
    """
    Plot 2D data. For example, 2d music scan. Data is expected to be 1D and to be reshaped further in this class
    """
    def __init__(self,
                 title: str,
                 x_label: str,
                 y_label: str,
                 x_data: np.array,
                 y_data: np.array,
                 x_extent: str = None,
                 y_extent: str = None,
                 port_size=4):
        """
        Initializes a single line plotter
        :param title: The title of the plotter
        :param x_label: The x-label of the plotter
        :param y_label: The y-label for the plotter
        :param x_extent: The visual x-range of the plotter
        :param y_extent: The visual y-range for the plotter
        :param x_data: The x-data of the plot
        :param y_data: The y-data of the plot
        """
        QMainWindow.__init__(self)
        pipeline.Stage.__init__(self, 1, port_size, None, has_process=False)

        # Layout
        self.setWindowTitle('Real-Time Pcolormesh Plot')
        self.setGeometry(100, 100, 800, 600)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.plot_widget = pg.PlotWidget()
        self.layout.addWidget(self.plot_widget)
        self.mesh = pg.PColorMeshItem()
        self.plot_widget.addItem(self.mesh)

        # Styling
        self.plot_widget.setTitle(title, color='black', size='18pt')
        self.plot_widget.setLabel('left', y_label, color='black', size='20pt')
        self.plot_widget.setLabel('bottom', x_label, color='black', size='20pt')
        self.plot_widget.showGrid(x=True, y=True)
        self.x_extent = x_extent
        self.y_extent = y_extent

        # Data
        self.x_data, self.y_data = x_data, y_data
        self.xx_data, self.yy_data = np.meshgrid(self.x_data, self.y_data)

        # Make a timer to update plot
        self.timer = QTimer()
        self.timer.setInterval(0)
        self.timer.timeout.connect(self._on_frame_update)
        self.timer.start()

    def _on_frame_update(self):
        """
        Called every frame update. Called by the timer
        :return: None
        """
        data = self.port_get()[0]
        data = np.reshape(data, self.xx_data.shape)
        self.mesh.setData(data)
