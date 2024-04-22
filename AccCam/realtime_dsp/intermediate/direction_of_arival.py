import AccCam.direction_of_arival as doa
import AccCam.realtime_dsp.pipeline as pipe
import numpy as np


class DelaySumBeamformer(pipe.Stage):
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
        direction = doa.delay_sum_beamformer(data, self.steering_matrix)
        self.port_put(pipe.Message(direction))


class BartlettBeamformer(pipe.Stage):
    """
    Implements a Bartlett beamformer to a stage
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
        direction = doa.bartlett_beamformer(data, self.steering_matrix)
        self.port_put(pipe.Message(direction))


class MVDRBeamformer(pipe.Stage):
    """
    Implements a Minimum Variance Distortionless Response (MVDR) beamformer to a stage
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
        direction = doa.mvdr_beamformer(data, self.steering_matrix)
        self.port_put(pipe.Message(direction))


class MSNRBeamformer(pipe.Stage):
    """
    Implements a Minimum Signal to Noise Ratio (MVDR) beamformer to a stage
    """

    def __init__(self,
                 steering_matrix: doa.SteeringMatrix,
                 noise_covariance: np.array,
                 port_size=4,
                 destinations=None):
        """
        :param steering_matrix: The steering matrix for the beamformer
        :param noise_covariance: The covariance matrix of the noise
        """
        super().__init__(1, port_size, destinations)
        self.steering_matrix = steering_matrix
        self.noise_covariance = noise_covariance

    def run(self):
        message = self.port_get()[0]
        data = message.payload
        direction = doa.msnr_beamformer(data, self.steering_matrix, self.noise_covariance)
        self.port_put(pipe.Message(direction))


class LCMVBeamformer(pipe.Stage):
    """
    Implements a Linearly Constrained Minimum Variance (LCMV) beamformer to a stage
    """

    def __init__(self,
                 steering_matrix: doa.SteeringMatrix,
                 constraints: np.array,
                 port_size=4,
                 destinations=None):
        """
        :param steering_matrix: The steering matrix for the beamformer
        :param constraints: The linear constraints on the beamformer response
        """
        super().__init__(1, port_size, destinations)
        self.steering_matrix = steering_matrix
        self.constrains = constraints

    def run(self):
        message = self.port_get()[0]
        data = message.payload
        direction = doa.lcmv_beamformer(data, self.steering_matrix, self.constrains)
        self.port_put(pipe.Message(direction))


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
        :param steering_matrix: The steering matrix to utilize to find the sources
        :param num_sources: The number of signals in the environment
        """
        super().__init__(1, port_size, destinations)
        self.steering_matrix = steering_matrix
        self.num_sources = num_sources

    def run(self):
        message = self.port_get()[0]
        data = message.payload
        direction = doa.music(data, self.steering_matrix, self.num_sources)
        self.port_put(pipe.Message(direction))


# WIP
class WidebandMusic(pipe.Stage):
    """
    Implements the MUSIC (MUltiple SIgnal Classification) algorithm to a stage
    """

    def __init__(self,
                 steering_matrix: doa.SteeringMatrix,
                 num_sources: int,
                 wavenumber_range: tuple[float],
                 port_size=4,
                 destinations=None):
        """
        :param steering_matrix: The steering matrix to utilize to find the sources
        :param num_sources: The number of signals in the environment
        :param wavenumber_range: The range (min, max) of wavenumbers to include in the band. SteeringMatrix.wavenumber
            should be in the middle of this band.
        """
        super().__init__(1, port_size, destinations)
        self.steering_matrix = steering_matrix
        self.num_sources = num_sources
        self.wavenumber_range = wavenumber_range

    def run(self):
        message = self.port_get()[0]
        data = message.payload
        direction = doa.wideband_music(data, self.steering_matrix, self.num_sources, self.wavenumber_range)
        self.port_put(pipe.Message(direction))
