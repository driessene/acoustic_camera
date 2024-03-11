import multiprocessing as mp


class Stage(mp.Process):
    def __init__(self, destinations=None, num_inputs=1, queue_size=4):
        super().__init__()
        self.destinations = destinations or []
        self.input_queue = [mp.Queue(queue_size) for _ in range(num_inputs)]

    def input_queue_get(self):
        return [queue.get() for queue in self.input_queue]

    def destination_queue_put(self, data):
        for destination in self.destinations:
            destination.put(data)
