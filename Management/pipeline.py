import multiprocessing as mp
import matplotlib.pyplot as plt


class Source:
    def __init__(self, queue_size=4):
        self.out_queue = mp.Queue(queue_size)

    def out_queue_get(self, block=True, timeout=None):
        return self.out_queue.get(block, timeout)

    def out_queue_put(self, data):
        self.out_queue.put(data)

    def clear_out_queue(self):
        while not self.out_queue.empty():
            self.out_queue.get()


class Sink:
    def __init__(self, queue_size=4):
        self.in_queue = mp.Queue(queue_size)

    def in_queue_get(self, block=True, timeout=None):
        return self.in_queue.get(block, timeout)

    def in_queue_put(self, data):
        self.in_queue.put(data)

    def clear_in_queue(self):
        while not self.in_queue.empty():
            self.in_queue.get()


class Process(Source, Sink):
    def __init__(self, queue_size=4):
        Source.__init__(self, queue_size=queue_size)
        Sink.__init__(self, queue_size=queue_size)


class AudioPipeline:
    def __init__(self,
                 recorder,          # recorders type
                 filters: list,     # filters type
                 algorithms: list,  # direction_of_arrival type
                 plotters: list):   # plotters type
        self.recorder = recorder
        self.filters = filters
        self.algorithms = algorithms
        self.plotters = plotters

        # Start processes
        self.recorder.start()
        for filter in self.filters:
            filter.start()
        for algorithm in self.algorithms:
            algorithm.start()


    def flowpath(self):
        # THIS IS EXTREMELY GENERIC!!
        # Make a subclass to alter this
        # Each object in this path must inherit a sink, source, or process from above
        # Use the corresponding queues to manage multiprocessing

        while True:
            # Get recording data
            data = self.recorder.get()

            # Apply filters
            for f in self.filters:
                f.put(data)
                data = f.get()

            # Apply algorithms
            algorithm_outputs = []
            for algo in self.algorithms:
                algo.in_queue_put(data)
                algorithm_outputs.append(algo.get())

            # Plot
            for (algo, plot) in zip(algorithm_outputs, self.plotters):
                plot.in_queue_put(algo)

    def start(self):
        self.recorder.start()
        plt.ion()
        plt.show(block=False)
        while True:
            self.flowpath()
