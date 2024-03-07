import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation


class LinePlotter:
    def __init__(self, xlim, ylim, interval):
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
        self.data = []

    def set_data(self, data):
        self.data = data

    def _update(self, frame):
        line_data = self.data
        self.line.set_data(np.linspace(self.xlim[0], self.xlim[1], len(line_data)), line_data)
        return self.line,

    @staticmethod
    def show():
        plt.show()

    @staticmethod
    def close():
        plt.close()

class MultiLinePlotter:
    def __init__(self, xlim, ylim, lines, interval):
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
        self.data = []
        self.ax.legend(loc='upper right')

    def set_data(self, data):
        self.data = data

    def _update(self, frame):
        for i, line in enumerate(self.lines):
            line_data = self.data[:, i]
            line.set_data(np.linspace(self.xlim[0], self.xlim[1], len(line_data)), line_data)
        return self.lines,

    @staticmethod
    def show():
        plt.show()

    @staticmethod
    def close():
        plt.close()
