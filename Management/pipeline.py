import multiprocessing as mp
import numpy as np


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

    def port_put(self, data):
        """
        Puts data to all destinations
        :param data: Data to put
        :return: None
        """
        for destination in self.destinations:
            destination.put(data)


class ChannelPicker(Stage):
    """
    takes and input matrix, picks a channel, and pushes the channel
    """
    def __init__(self, channel, port_size=4, destinations=None):
        """
        :param channel: The channel to push
        :param port_size: Size of the queues
        :param destinations: Other object input queue to push to
        """
        super().__init__(1, port_size, destinations, True)
        self.channel = channel

    def run(self):
        self.port_put(self.port_get()[0][:, self.channel])


class Bus(Stage):
    """
    Takes several inputs, warps data into a tuple, pushes to destinations
    """
    def __init__(self, num_ports, port_size, destinations):
        """
        :param num_ports: Number of ports on the bus
        :param port_size: Size of the queues
        :param destinations: Other object input queue to push to
        """
        super().__init__(num_ports, port_size, destinations)

    def run(self):
        self.port_put(tuple(self.port_get()))


class Concatenator(Stage):
    """
    Takes several inputs, concatenates, pushes to destinations
    """
    def __init__(self, num_ports, port_size=4, destinations=None):
        """
        Initializes a concatinator
        :param num_ports: Number of ports on the bus
        :param port_size: Size of the queues
        :param destinations: Other object input queue to push to
        """
        super().__init__(num_ports, port_size, destinations)

    def run(self):
        self.port_put(np.concatenate(self.port_get(), axis=1))
