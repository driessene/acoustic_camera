import numpy as np
from AccCam.direction_of_arrival.geometry import SteeringMatrix
from abc import ABC, abstractmethod


def get_covariance(data: np.array) -> np.array:
    """
    Get the covariance of the input data. Always transpose for this project.
    :param data: Input data to compute covariance of
    :return: np.array
    """
    return np.cov(data.T)


def get_noise_subspace(cov_data: np.array, num_sources: int) -> np.array:
    """
    Find the noise subspace of a provided signal
    :param cov_data: The covariance matrix to find the noise subspace of
    :param num_sources: The number of sources in the environment
    :return: np.array
    """
    # Decompose into eigenvalues and vectors
    eigvals, eigvecs = np.linalg.eigh(cov_data)

    # Get smallest eigenvectors
    noise_subspace = eigvecs[:, np.argsort(eigvals)][:, :-num_sources]
    return noise_subspace


class Estimator(ABC):
    """
    Holds a beamformer. Use as a subclass for beamformers.
    """
    def __init__(self, steering_matrix):
        """
        :param steering_vector: The steering matrix to utilize to find the sources
        """
        self.steering_matrix = steering_matrix

    @abstractmethod
    def process(self, data: np.array) -> np.array:
        """
        Preform calcuations here
        :param data: The source data
        :return: np.array
        """
        pass


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
        # Get covariance matrix
        cov_matrix = get_covariance(data)

        # Get noise subspace
        noise_subspace = get_noise_subspace(cov_matrix, self.num_sources)

        # Compute the music spectrum. Use np.sum to take several samples into one result
        music_spectrum = 1 / np.sum(np.abs(self.steering_matrix.matrix.conj().T @ noise_subspace) ** 2, axis=1)

        # Normalize and return results
        music_spectrum /= np.max(music_spectrum)
        return music_spectrum
