import pyqtgraph as pg
from Management import pipeline
import numpy as np
from PyQt5 import QtCore, QtWidgets
from time import perf_counter


class SingleLinePlotter(QtWidgets.QMainWindow, pipeline.Stage):
    def __init__(self,
                 title: str,
                 x_label: str,
                 y_label: str,
                 x_range: tuple,
                 y_range: tuple,
                 interval: int,
                 queue_size=4
                 ):
        QtWidgets.QMainWindow.__init__(self)
        pipeline.Stage.__init__(self, num_inputs=1, queue_size=queue_size)

        # Performance tracking
        self.last_time = perf_counter()
        self.delta_time = 0
        self.fps_array = np.zeros(100)

        # Styling
        self.plot_graph = pg.PlotWidget()
        self.setCentralWidget(self.plot_graph)
        self.plot_graph.setBackground('black')
        self.plot_graph.setTitle(title, color='white', size='18pt')
        self.plot_graph.setLabel('left', y_label, color='white', size='20pt')
        self.plot_graph.setLabel('bottom', x_label, color='white', size='20pt')
        self.plot_graph.showGrid(x=True, y=True)
        self.x_range = x_range
        self.y_range = y_range
        self.plot_graph.setXRange(x_range[0], x_range[1])
        self.plot_graph.setYRange(y_range[0], y_range[1])

        # Data
        self.line_data = ([0, 0], [0, 0])
        self.line = self.plot_graph.plot(
            self.line_data[0],
            self.line_data[1],
            name='Data',
            pen=pg.mkPen(color='white', width=2)
        )

        # info footer
        self.footer = QtWidgets.QLabel()
        self.footer.setText('Update Rate: 0.0 FPS\nItems in Queue: 0')  # Initial display
        self.footer.setStyleSheet("color: black; font-size: 12pt;")
        self.statusBar().addWidget(self.footer)  # Add to status bar

        # Make a timer to update plot
        self.interval = interval
        self.timer = QtCore.QTimer()
        self.timer.setInterval(self.interval)
        self.timer.timeout.connect(self.run)
        self.timer.start()

    def run(self):
        # Update FPS
        self.delta_time = perf_counter() - self.last_time
        self.last_time = perf_counter()
        self.fps_array = np.append(self.fps_array, 1 / self.delta_time)
        self.fps_array = np.delete(self.fps_array, 0)
        fps = np.average(self.fps_array)

        # Update footer
        queue_size = self.input_queue[0].qsize()  # Get current queue size
        self.footer.setText(f'Update Rate: {fps:.2f} FPS\nQueue Size: {queue_size}')

        # Update data queue
        data = self.input_queue_get()[0].get()
        self.line_data = (np.linspace(self.x_range[0], self.x_range[1], len(data)), data)
        self.line.setData(*self.line_data)
