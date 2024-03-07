import threading
from DSP import plotters, filters, recorders, direction_of_arrival


class AudioPipeline:
    def __init__(self,
                 recorder: recorders,
                 filters: list[filters],
                 dsp_algorithms: list[direction_of_arrival],
                 plotters: list[plotters]):
        self.recorder = recorder
        self.filters = filters
        self.dsp_algorithms = dsp_algorithms
        self.plotters = plotters
        self.thread = threading.Thread(target=self._update)

    def flowpath(self):
        """     EXAMPLE
        # Get data
        data = self.recorder.pop()

        # Apply filters
        for f in self.filters:
            data = f.process(data)

        # Apply algorithms
        results = []
        for algo in self.dsp_algorithms:
            results.append(algo.process())

        # Plot results
        for result, plot in zip(self.plotters, results):
            plot.setData(result)
        """
        raise NotImplementedError   # subclass must implement this


    def _update(self):
        while True:
            self.flowpath()

    def start(self):
        self.recorder.start()
        self.thread.start()
        self.plotters[0].show()

    def stop(self):
        self.recorder.stop()
