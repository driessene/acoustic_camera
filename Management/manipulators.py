from pipeline import Stage
from numpy import concatenate

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
        self.port_put(concatenate(self.port_get(), axis=1))
