import config

if config.USE_CUPY:
    import cupy as np
else:
    import numpy as np

import pipeline


class ChannelPicker(pipeline.Stage):
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
        self.port_put(pipeline.Message(self.port_get()[0].payload[:, self.channel]))


class Bus(pipeline.Stage):
    """
    Takes several messages, warps data into a tuple, pushes to destinations
    """
    def __init__(self, num_ports, port_size, destinations):
        """
        :param num_ports: Number of ports on the bus
        :param port_size: Size of the queues
        :param destinations: Other object input queue to push to
        """
        super().__init__(num_ports, port_size, destinations)

    def run(self):
        self.port_put(pipeline.Message(tuple(self.port_get())))


class Concatenator(pipeline.Stage):
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
        # Get message, get payloads, concatenate, put into message, put to port
        self.port_put(pipeline.Message(np.concatenate([data.payload for data in self.port_get()], axis=1)))
