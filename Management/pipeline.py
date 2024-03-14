import multiprocessing as mp


class Stage(mp.Process):
    """
    Manages processes (nodes) in a pipeline. Each node runs in a loop, taking input data, processing it, and pushing
    it to other destinations' input queues. Destinations are not required, such as for plotters. Inputs are not
    required, such as for audio sources. Each process can have several inputs and destinations, making branching and
    merging possible.
    """
    def __init__(self, num_inputs=1, queue_size=4, destinations=None):
        """
        Initializes the process
        :param num_inputs: Number of input queues
        :param queue_size: The size of an imput queue
        :param destinations: Other object input queues to push results to
        """
        super().__init__()

        if destinations is None:
            destinations = []
        self.destinations = destinations
        self.input_queue = [mp.Queue(queue_size) for _ in range(num_inputs)]

    def link_to_destination(self, next_stage, port):
        """
        Adds a destination to push data too. This is easier to read in scripting rather than providing all destinations
        at onece
        :param next_stage: The object to send data to
        :param port: The input queue to send data to
        :return:
        """
        self.destinations.append(next_stage.input_queue[port])

    def input_queue_get(self):
        """
        Gets data from all input queues in a list
        :return: List
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
