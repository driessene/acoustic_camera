import AccCam.direction_of_arival as doa
import AccCam.realtime_dsp.pipeline as pipe


class Music(pipe.Stage):
    """
    Implements the MUSIC (MUltiple SIgnal Classification) algorithm to a stage
    """
    def __init__(self,
                 steering_matrix: doa.SteeringMatrix,
                 num_sources: int,
                 port_size=4,
                 destinations=None):
        """
        :param steering_matrix: ___
        :param num_sources: The number of signals in the environment
        :param port_size: The size of the input queue
        :param destinations: Where to push output data. Object should inherit Stage
        """
        super().__init__(1, port_size, destinations)
        self.steering_matrix = steering_matrix
        self.num_sources = num_sources

    def run(self):
        message = self.port_get()[0]
        data = message.payload
        direction = doa.music(data, self.steering_matrix, self.num_sources)
        self.port_put(pipe.Message(direction))


class Beamformer(pipe.Stage):
    """
    Implements a delay-and-sum (conventional) beamformer to a stage
    """
    def __init__(self,
                 steering_matrix: doa.SteeringMatrix,
                 port_size=4,
                 destinations=None):
        """
        :param steering_matrix: The steering matrix for the beamformer
        """
        super().__init__(1, port_size, destinations)
        self.steering_matrix = steering_matrix

    def run(self):
        message = self.port_get()[0]
        data = message.payload
        direction = doa.Beamformer(data, self.steering_matrix)
        self.port_put(pipe.Message(direction))
