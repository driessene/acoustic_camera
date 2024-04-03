import multiprocessing as mp
import numpy as np


class Stage:
    def __init__(self, num_ports=1, queue_size=4, destinations=None, has_process=True):
        """
        Initializes the process
        :param num_ports: Number of input queues
        :param queue_size: The size of an input queue
        :param destinations: Other object input queues to push results to
        """
        super().__init__()

        if destinations is None:
            destinations = []
        self.destinations = destinations
        self.input_queue = [mp.Queue(queue_size) for _ in range(num_ports)]

        if has_process:
            self.process = mp.Process(target=self.run)

    def run(self):
        """
        Function that the process will run. Must be implemented by a subclass
        :return: None
        """
        raise NotImplementedError

    def start(self):
        if self.process:
            self.process.start()

    def link_to_destination(self, next_stage, port):
        """
        Adds a destination to push data too. This is easier to read in scripting rather than providing all destinations
        at once
        :param next_stage: The object to send data to
        :param port: The input queue to send data to
        :return: None
        """
        self.destinations.append(next_stage.input_queue[port])

    def input_queue_get(self):
        """
        Gets data from all input queues in a list
        :return: list
        """
        return [queue.get() for queue in self.input_queue]

    def destination_queue_put(self, data):
        """
        Puts data to all destinations
        :param data: Data to put
        :return: None
        """
        for destination in self.destinations:
            destination.put(data)


class Bus(Stage):
    """
    Takes several inputs, warps data into a tuple, pushes to destinations
    """
    def __init__(self, num_ports, queue_size, destinations):
        """
        Initializes a bus
        :param num_ports: Number of ports on the bus
        :param queue_size: Size of the queues
        :param destinations: Other object input queue to push to
        """
        super().__init__(num_ports, queue_size, destinations)

    def run(self):
        self.destination_queue_put(tuple(self.input_queue_get()))


class Concatenator(Bus):
    """
    Takes several inputs, concatenates, pushes to destinations
    """
    def __init__(self, num_ports, queue_size=4, destinations=None):
        """
        Initializes a concatinator
        :param num_ports: Number of ports on the bus
        :param queue_size: Size of the queues
        :param destinations: Other object input queue to push to
        """
        super().__init__(num_ports, queue_size, destinations)

    def run(self):
        self.destination_queue_put(np.concatenate(self.input_queue_get(), axis=1))
