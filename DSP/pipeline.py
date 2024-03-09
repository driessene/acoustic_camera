import multiprocessing as mp
from DSP import plotters, filters, recorders, direction_of_arrival


class Source:
    def __init__(self, queue_size=4):
        self.out_queue = mp.Queue(queue_size)

    def get(self):
        return self.out_queue.get()

    def clear_out_queue(self):
        while not self.out_queue.empty():
            self.out_queue.get()


class Sink:
    def __init__(self, queue_size=4):
        self.in_queue = mp.Queue(queue_size)

    def put(self, data):
        self.in_queue.put(data)

    def clear_in_queue(self):
        while not self.in_queue.empty():
            self.in_queue.get()


class Process(Source, Sink):
    def __init__(self, queue_size=4):
        super().__init__(queue_size)


class AudioPipeline:
    def __init__(self,
                 recorder: recorders,
                 filters: list[filters],
                 algorithms: list[direction_of_arrival],
                 plotters: list[plotters]):
        self.recorder = recorder
        self.filters = filters
        self.algorithms = algorithms
        self.plotters = plotters
        self.process = mp.Process(target=self._process)

    def flowpath(self):
        # THIS IS EXTREMLY GENEARIC!!
        # Make a subclass to alter this
        # Each object in this path must inherit a sink, source, or process from above
        # Use the corresponding queues to manage multiprocessing

        # Get recording data
        data = self.recorder.get()

        # Apply filters
        for f in self.filters:
            f.put(data)
            data = f.get()

        # Apply algorithms
        algorithm_outputs = []
        for algo in self.algorithms:
            algo.put(data)
            algorithm_outputs.append(algo.get())

        # Plot
        for (algo, plot) in zip(algorithm_outputs, self.plotters):
            plot.put(algo)

    def _process(self):
        while True:
            self.flowpath()

    def start(self):
        self.recorder.start()
        self.process.start()
        self.plotters[0].show()

    def stop(self):
        self.recorder.stop()
