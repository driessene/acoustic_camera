import numpy as np
from AccCam.direction_of_arrival.geometry import Structure


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
    def __init__(self, structure):
        """
        :param steering_vector: The steering matrix to utilize to find the sources
        """
        self.structure = structure

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
    def __init__(self, structure: Structure):
        """
        :param structure: The steering matrix to utilize to find the sources
        """
        super().__init__(structure)

    def process(self, data: np.array) -> np.array:
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

    def process(self, data: np.array) -> np.array:
        cov_matrix = np.cov(data.T)
        beamformed_data = np.sum(self.structure.steering_matrix.conj().T *
                                 (cov_matrix @ self.structure.steering_matrix).T, axis=1).real

        # Normalize
        beamformed_data /= np.max(beamformed_data)
        return beamformed_data


class MVDRBeamformer(Estimator):
    """
    Implements a MVDR beamformer
    """
    def __init__(self, structure: Structure):
        """
        :param structure: The steering matrix to utilize to find the sources
        """
        super().__init__(structure)

    def process(self, data: np.array) -> np.array:
        cov_matrix = np.cov(data.T)
        beamformed_data = 1 / np.sum(self.structure.steering_matrix.conj().T *
                                     np.linalg.lstsq(
                                         cov_matrix,
                                         self.structure.steering_matrix,
                                         None)[0].T, axis=1).real

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

    def process(self, data: np.array) -> np.array:
        # Get noise subspace:
        noise_subspace = find_noise_subspace(data, self.num_sources)

        # Compute the music spectrum. Use np.sum to take several samples into one result
        music_spectrum = 1 / np.sum(np.abs(self.structure.steering_matrix.conj().T @ noise_subspace) ** 2, axis=1)

        # Normalize and return results
        music_spectrum /= np.max(music_spectrum)
        return music_spectrum
