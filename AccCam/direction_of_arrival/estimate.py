from AccCam.__config__ import __USE_CUPY__

if __USE_CUPY__:
    import cupy as np
else:
    import numpy as np

from AccCam.direction_of_arrival.geometry import Structure
from abc import ABC, abstractmethod


def calculate_covariance(data: np.ndarray) -> np.ndarray:
    """
    :param data: The signal matrix to find the covariance of
    :return: The covariance matrix of the signal matrix
    """
    return np.cov(data.T)


def calculate_noise_subspace(cov_data: np.ndarray, num_sources: int) -> np.ndarray:
    """
    Find the noise subspace of a provided signal
    :param cov_data: The covariance matrix to find the noise subspace of
    :param num_sources: The number of sources in the environment
    :return:
    """
    # Decompose into eigenvalues and vectors
    eigvals, eigvecs = np.linalg.eigh(cov_data)

    noise_subspace = eigvecs[:, np.argsort(eigvals)][:, :-num_sources]
    return noise_subspace


class Estimator(ABC):
    """
    Holds a beamformer. Use as a subclass for beamformers.
    """
    def __init__(self, structure: Structure):
        """
        :param structure: The steering matrix to utilize to find the sources
        """
        self.structure = structure

    @abstractmethod
    def process(self, data: np.ndarray) -> np.ndarray:
        """
        Preform calculations here
        :param data: The source data
        :return: Estimated locations in a 2d matrix with the same shape as the steering matrix.
        """
        raise NotImplementedError


class DelaySumBeamformer(Estimator):
    """
    Implements a delay-and-sum (conventional) beamformer
    """
    def __init__(self, structure: Structure):
        """
        :param structure: The steering matrix to utilize to find the sources
        """
        super().__init__(structure)

    def process(self, data: np.ndarray) -> np.ndarray:
        # Delay and sum
        beamformed_data = np.var(self.structure.steering_matrix.conj().T @ data.T, axis=1).real

        # Normalize
        beamformed_data /= np.max(beamformed_data)
        return beamformed_data


class BartlettBeamformer(Estimator):
    """
    Implements a bartlett beamformer
    """
    def __init__(self, structure: Structure):
        """
        :param structure: The steering matrix to utilize to find the sources
        """
        super().__init__(structure)

    def process(self, data: np.ndarray) -> np.ndarray:
        # Bartlett formula
        cov_matrix = calculate_covariance(data)
        beamformed_data = np.sum(self.structure.steering_matrix.conj().T *
                                 (cov_matrix @ self.structure.steering_matrix).T, axis=1).real

        # Normalize
        beamformed_data /= np.max(beamformed_data)
        return beamformed_data


class MVDRBeamformer(Estimator):
    """
    Implements a Minimum Variance Distortionless Response (MVDR) beamformer
    """
    def __init__(self, structure: Structure):
        """
        :param structure: The steering matrix to utilize to find the sources
        """
        super().__init__(structure)

    def process(self, data: np.ndarray) -> np.ndarray:
        # Get covariance
        cov_matrix = calculate_covariance(data)

        # Find minimum response
        beamformed_data = 1 / np.sum(
            self.structure.steering_matrix.conj().T *
            np.linalg.lstsq(
                cov_matrix,
                self.structure.steering_matrix,
                None)[0].T,
            axis=1).real

        # Normalize
        beamformed_data /= np.max(beamformed_data)
        return beamformed_data


class Music(Estimator):
    """
    Implements the MUSIC (MUltiple SIgnal Classification) algorithm
    """
    def __init__(self, structure: Structure, num_sources: int):
        """
        :param num_sources: The number of sources to find.
        """
        super().__init__(structure)
        self.num_sources = num_sources

    def process(self, data: np.ndarray) -> np.ndarray:
        # Calculate covariance
        cov_matrix = calculate_covariance(data)

        # Get noise subspace:
        noise_subspace = calculate_noise_subspace(cov_matrix, self.num_sources)

        # Compute the music spectrum. Use np.sum to take several samples into one result
        music_spectrum = 1 / np.sum(np.abs(self.structure.steering_matrix.conj().T @ noise_subspace) ** 2, axis=1)

        # Normalize and return results
        music_spectrum /= np.max(music_spectrum)
        return music_spectrum
