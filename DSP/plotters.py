import matplotlib.pyplot as plt
import numpy as np
from _queue import Empty
from matplotlib.animation import FuncAnimation
from Management.pipeline import Sink


class LinePlotter(Sink):
    def __init__(self, xlim, ylim, interval, queue_size=4):
        super().__init__(queue_size)
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.line, = self.ax.plot([], [], lw=2)
        self.xlim = xlim
        self.ylim = ylim
        self.ax.set_ylim(*ylim)
        self.ax.set_xlim(*xlim)
        self.interval = interval
        self.ani = FuncAnimation(
            fig=self.fig,
            func=self._update,
            frames=None,
            interval=self.interval,
            blit=False
        )

    def _update(self, frame):
        try:
            line_data = self.in_queue_get(block=False)
        except Empty:
            # Handle the case when the queue is empty
            return self.line,

        self.line.set_data(np.linspace(self.xlim[0], self.xlim[1], len(line_data)), line_data)
        return self.line,

    @staticmethod
    def show():
        plt.show()

    @staticmethod
    def close():
        plt.close()


class MultiLinePlotter(Sink):
    def __init__(self, xlim, ylim, lines, interval, queue_size=4):
        super().__init__(queue_size)
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.lines = [self.ax.plot([], [], lw=2, label=f'Channel {i}')[0] for i in range(lines)]
        self.xlim = xlim
        self.ylim = ylim
        self.ax.set_ylim(*ylim)     # set y lims
        self.ax.set_xlim(*xlim)     # Set x lims
        self.interval = interval
        self.ani = FuncAnimation(
            fig=self.fig,
            func=self._update,
            frames=None,
            interval=self.interval,
            blit=False
        )
        self.ax.legend(loc='upper right')

    def _update(self, frame):
        try:
            data = self.in_queue_get(block=False)
        except Empty:
            # Handle the case when the queue is empty
            return self.lines,

        for i, line in enumerate(self.lines):
            line_data = data[:, i]
            line.set_xdata(np.linspace(self.xlim[0], self.xlim[1], len(line_data)))
            line.set_ydata(line_data)
        return self.lines,

    @staticmethod
    def show():
        plt.show()

    @staticmethod
    def close():
        plt.close()
