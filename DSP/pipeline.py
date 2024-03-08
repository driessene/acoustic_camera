import multiprocessing as mp
from DSP import plotters, filters, recorders, direction_of_arrival


class AudioPipeline:
    def __init__(self,
                 recorder: recorders,
                 filters: list[filters],
                 dsp_algorithms: list[direction_of_arrival],
                 plotters: list[plotters],
                 num_processes: int = 4):
        self.recorder = recorder
        self.filters = filters
        self.dsp_algorithms = dsp_algorithms
        self.plotters = plotters
        self.processes = [mp.Process(target=self._update) for i in range(num_processes)]

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

        # DO NOT PROCESS RESULTS IN HERE!!!
        # rather, call self.sink()
        """
        raise NotImplementedError   # subclass must implement this


    def _update(self):
        while True:
            self.flowpath()

    def start(self):
        self.recorder.start()
        for process in self.processes:
            process.start()
        self.plotters[0].show()

    def stop(self):
        self.recorder.stop()
        for process in self.processes:
            process.terminate()
