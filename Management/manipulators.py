import numpy as np
from .pipeline import Stage, Message
import logging
from itertools import combinations

# Logging
logger = logging.getLogger(__name__)


def max_delta(messages: list[Message]) -> tuple[tuple, float]:
    """
    Returns the max delta pair of a list and its value
    :param messages: The messages to find the difference of
    :return:
    """
    timestamps = [message.timestamp for message in messages]
    max_delta_t_pair = max(combinations(timestamps, 2), key=lambda sub: abs(sub[0] - sub[1]))
    max_delta_t = abs(max_delta_t_pair[0] - max_delta_t_pair[1])
    return max_delta_t_pair, max_delta_t


def verifty_timestamps(messages: list[Message], threshold: float):
    """
    Verify the time integrity of data
    :param messages: The messages received
    :return: Threshold in seconds to raise a warning
    """
    try:
        timestamps = [message.timestamp for message in messages]
        pair, value = max_delta(timestamps)
        if value > threshold:  # 1 millisecond
            logger.warning(f'Messages {pair} had a time delta of {value * 1000} milliseconds')

    except KeyError:
        logging.warning('Time delta could not be calculated')


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
        self.port_put(Message(self.port_get()[0].payload[:, self.channel]))


class Bus(Stage):
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
        messages = self.port_get()
        verifty_timestamps(messages, 1)

        self.port_put(Message(tuple(messages)))


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
        # Get message
        messages = self.port_get()
        verifty_timestamps(messages, 1)

        self.port_put(Message(np.concatenate([message.payload for message in messages], axis=1)))
