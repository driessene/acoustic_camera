import multiprocessing as mp
from datetime import datetime
from abc import ABC


class Message:
    """
    A message class for transferring  data between stages in a pipeline.
    """
    def __init__(self, payload, timestamp=None, **kwargs):
        """
        :param payload: Main data to be sent to a stage
        :param timestamp: The time the message was sent. Automatically set
        :param kwargs: Other information about the message
        """
        self.payload = payload
        self.timestamp = timestamp

        for k, v in kwargs.items():
            setattr(self, k, v)


class Stage(ABC):
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
        To be implemented by a subclass. Ran in a loop forever. This is the script the subclass will run. If a process
        is not needed (plotters, sounddevice stages), ignore this.
        :return: None
        """
        pass

    def start(self):
        """
        Start the stage
        :return: None
        """
        if self.process:
            self.process.start()

    def stop(self):
        """
        Stop the stage
        :return: None
        """
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
        :return: list[Message]
        """
        return [queue.get() for queue in self.input_queue]

    def port_put(self, message: Message):
        """
        Puts data to all destinations
        :param message: Message to put
        :return: None
        """
        message.timestamp = datetime.now()
        for destination in self.destinations:
            destination.put(message)
