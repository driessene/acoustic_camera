import numpy as np
from AccCam.direction_of_arrival.geometry import SteeringMatrix


def find_noise_subspace(data: np.array, num_sources: int) -> np.array:
    """
    Find the noise subspace of a provided signal
    :param data: The signal to find the noise subspace of
    :param num_sources: The number of sources in the environment
    :return:
    """
    # Calculate the covariance matrix
    Rx = np.cov(data.T)

    # Decompose into eigenvalues and vectors
    eigvals, eigvecs = np.linalg.eigh(Rx)

    noise_subspace = eigvecs[:, np.argsort(eigvals)][:, :-num_sources]
    return noise_subspace




class Estimator:
    """
    Holds a beamformer. Use as a subclass for beamformers.
    """
    def __init__(self, steering_matrix):
        """
        :param steering_vector: The steering matrix to utilize to find the sources
        """
        self.steering_matrix = steering_matrix

    def process(self, data: np.array) -> np.array:
        """
        Preform calcuations here
        :param data: The source data
        :return: np.array
        """
        raise NotImplementedError


class DelaySumBeamformer(Estimator):
    """
    Implements a delay-and-sum (conventional) beamformer
    """
    def __init__(self, steering_matrix: SteeringMatrix):
        """
        :param steering_matrix: The steering matrix to utilize to find the sources
        """
        super().__init__(steering_matrix)

    def process(self, data: np.array) -> np.array:
        beamformed_data = np.var(self.steering_matrix.matrix.conj().T @ data.T, axis=1).real

        # Normalize
        beamformed_data /= np.max(beamformed_data)
        return beamformed_data


class BartlettBeamformer(Estimator):
    """
    Implements a bartlett beamformer
    """
    def __init__(self, steering_matrix: SteeringMatrix):
        """
        :param steering_matrix: The steering matrix to utilize to find the sources
        """
        super().__init__(steering_matrix)

    def process(self, data: np.array) -> np.array:
        cov_matrix = np.cov(data.T)
        beamformed_data = np.sum(self.steering_matrix.matrix.conj().T *
                                 (cov_matrix @ self.steering_matrix.matrix).T, axis=1).real

        # Normalize
        beamformed_data /= np.max(beamformed_data)
        return beamformed_data


class MVDRBeamformer(Estimator):
    """
    Implements a MVDR beamformer
    """
    def __init__(self, steering_matrix: SteeringMatrix):
        """
        :param steering_matrix: The steering matrix to utilize to find the sources
        """
        super().__init__(steering_matrix)

    def process(self, data: np.array) -> np.array:
        cov_matrix = np.cov(data.T)
        beamformed_data = 1 / np.sum(self.steering_matrix.matrix.conj().T *
                                     np.linalg.lstsq(
                                         cov_matrix,
                                         self.steering_matrix.matrix,
                                         None)[0].T, axis=1).real

        # Normalize
        beamformed_data /= np.max(beamformed_data)
        return beamformed_data


# WIP
class MSNRBeamformer(Estimator):
    """
    Implements a maximum signal-to-noise ratio (MSNR) beamformer
    """
    def __init__(self, steering_matrix: SteeringMatrix, noise_covariance):
        """
        :param steering_matrix: The steering matrix to utilize to find the sources
        :param noise_covariance: A covariance array representing the noise of the environment. If unknow, use
            np.eye(num_elements) * noise_power.
        """
        super().__init__(SteeringMatrix)
        self.noise_covariance = noise_covariance

    def process(self, data: np.array) -> np.array:
        noise_cov_inv = np.linalg.inv(self.noise_covariance)
        beamformed_data = np.sum(self.steering_matrix.matrix.conj().T *
                                 (noise_cov_inv @ self.steering_matrix.matrix).T, axis=1).real

        # Normalize
        beamformed_data /= np.max(beamformed_data)
        return beamformed_data


class Music(Estimator):
    """
    Implements the MUSIC (MUltiple SIgnal Classification) algorithm
    """
    def __init__(self, steering_matrix: SteeringMatrix, num_sources: int):
        """
        :param num_sources: The number of sources to find.
        """
        super().__init__(steering_matrix)
        self.num_sources = num_sources

    def process(self, data: np.array) -> np.array:
        # Get noise subspace
        noise_subspace = find_noise_subspace(data, self.num_sources)

        # Compute the music spectrum. Use np.sum to take several samples into one result
        music_spectrum = 1 / np.sum(np.abs(np.dot(self.steering_matrix.matrix.conj().T, noise_subspace)) ** 2, axis=1)

        # Normalize and return results
        music_spectrum /= np.max(music_spectrum)
        return music_spectrum
