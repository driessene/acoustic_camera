import multiprocessing as mp


class Process(mp.Process):
    def __init__(self, destinations: tuple, num_inputs=1, queue_size=4):
        super().__init__()
        self.destinations = destinations
        self.input_queue = (mp.Queue(queue_size) for i in range(num_inputs))

    def get_input_object(self):
        return (queue.get() for queue in self.input_queue)

    def put_output_object(self, data):
        for destination in self.destinations:
            destination.put(data)
