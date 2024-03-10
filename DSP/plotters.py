import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
import multiprocessing as mp


class LinePlotter:
    def __init__(self, in_queue: mp.Queue, xlim: tuple, ylim: tuple, interval: float):
        self.in_queue = in_queue
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.line, = self.ax.plot([], [], lw=2)
        self.xlim = xlim
        self.ylim = ylim
        self.ax.set_ylim(*ylim)
        self.ax.set_xlim(*xlim)
        self.interval = interval
        self.ani = FuncAnimation(
            fig=self.fig,
            func=self.run,
            frames=None,
            interval=self.interval,
            blit=False
        )

    def run(self, frame):
        line_data = self.in_queue.get()
        self.line.set_data(np.linspace(self.xlim[0], self.xlim[1], len(line_data)), line_data)
        return self.line,


class MultiLinePlotter:
    def __init__(self, in_queue: mp.Queue, xlim: tuple, ylim: tuple, lines: int, interval: float):
        self.in_queue = in_queue
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.lines = [self.ax.plot([], [], lw=2, label=f'Channel {i}')[0] for i in range(lines)]
        self.xlim = xlim
        self.ylim = ylim
        self.ax.set_ylim(*ylim)     # set y lims
        self.ax.set_xlim(*xlim)     # Set x lims
        self.interval = interval
        self.ani = FuncAnimation(
            fig=self.fig,
            func=self.run,
            frames=None,
            interval=self.interval,
            blit=False
        )
        self.ax.legend(loc='upper right')

    def run(self, frame):
        data = self.in_queue.get()

        for i, line in enumerate(self.lines):
            line_data = data[:, i]
            line.set_xdata(np.linspace(self.xlim[0], self.xlim[1], len(line_data)))
            line.set_ydata(line_data)
        return self.lines,
