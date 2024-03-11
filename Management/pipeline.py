import multiprocessing as mp


class Stage(mp.Process):
    def __init__(self, num_inputs=1, queue_size=4, destinations=None):
        super().__init__()

        if destinations is None:
            destinations = []
        self.destinations = destinations
        self.input_queue = [mp.Queue(queue_size) for _ in range(num_inputs)]

    def link_to_destination(self, next_stage, port):
        self.destinations.append(next_stage.input_queue[port])

    def input_queue_get(self):
        return [queue.get() for queue in self.input_queue]

    def destination_queue_put(self, data):
        for destination in self.destinations:
            destination.put(data)
