import multiprocessing as mp
import numpy as np


class Message:
    """
    A message class for transferring  data between stages in a pipeline.
    """
    def __init__(self, payload, **kwargs):
        self.payload = payload

        for k, v in kwargs.items():
            setattr(self, k, v)


class Stage:
    def __init__(self, num_ports=1, port_size=4, destinations=None, has_process=True):
        """
        Initializes the process
        :param num_ports: Number of input queues
        :param port_size: The size of an input queue
        :param destinations: Other object input queues to push results to
        """
        super().__init__()

        if destinations is None:
            destinations = []
        self.destinations = destinations
        self.input_queue = [mp.Queue(port_size) for _ in range(num_ports)]

        if has_process:
            self.process = mp.Process(target=self._process)
        else:
            self.process = None

    def _process(self):
        """
        Private, do not use. Encapsulates run in a while true loop. Intended to run forever, getting data, process,
        and push
        :return: None
        """
        while True:
            self.run()

    def run(self):
        """
        To be implemented by a subclass. Ran in a loop forever. This is the script the subclass will run
        :return:
        """
        raise NotImplementedError

    def start(self):
        if self.process:
            self.process.start()

    def stop(self):
        if self.process:
            self.process.terminate()
            self.process.join()

    def link_to_destination(self, next_stage, port):
        """
        Adds a destination to push data too. This is easier to read in scripting rather than providing all destinations
        at once
        :param next_stage: The object to send data to
        :param port: The input queue to send data to
        :return: None
        """
        self.destinations.append(next_stage.input_queue[port])

    def port_get(self):
        """
        Gets data from all input queues in a list
        :return: list
        """
        return [queue.get() for queue in self.input_queue]

    def port_put(self, data: Message):
        """
        Puts data to all destinations
        :param data: Data to put
        :return: None
        """
        for destination in self.destinations:
            destination.put(data)


class Message:
    """
    Use messages to pass data between stages. Allows for metadata
    """
    def __init__(self, payload, **kwargs):
        """
        :param payload: Payload to send to destination. Main set of data
        :param kwargs: Metadata. For example, a timestamp
        """
        self.payload = payload
        for key, value in kwargs.items():
            setattr(self, key, value)
