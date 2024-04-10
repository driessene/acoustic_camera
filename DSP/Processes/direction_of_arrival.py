from .. import config

if config.USE_CUPY:
    import cupy as np
else:
    import numpy as np
from Management import pipeline


class Beamform(pipeline.Stage):
    """
    A classical beamformer
    """
    def __init__(self, steering_matrix, port_size=4, destinations=None):
        """
        :param steering_matrix: ___
        :param port_size: The size of the input queue
        :param destinations: Where to push results. Object should inherit from Stage
        """
        super().__init__(1, port_size, destinations)
        self.steering_matrix = steering_matrix

    def run(self):
        """
        Runs the beamformer on input data. Ran by a process
        :return: None
        """
        # Beamformer
        data = self.port_get()[0]
        r_weighted = np.abs(self.steering_matrix.matrix.conj().T @ data.T) ** 2  # Beamforming output

        # Normalize results
        results = 10 * np.log10(np.var(r_weighted, axis=1))  # Power in signal, in dB
        results -= np.max(results)

        # Push X and Y data
        self.port_put(results)


class MUSIC(pipeline.Stage):
    """
    Implements the MUSIC (MUltiple SIgnal Classification) algorithm
    """
    def __init__(self, steering_matrix, num_sources, port_size=4, destinations=None):
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
        """
        Runs MUSIC on input data. Ran by a process
        :return: None
        """
        # Calculate the covariance matrix
        data = self.port_get()[0]
        Rx = np.cov(data.T)
        # Decompose into eigenvalues and vectors
        eigvals, eigvecs = np.linalg.eigh(Rx)

        # Sort eigenvalues and corresponding eigenvectors
        sorted_indices = np.argsort(eigvals)[::-1]  # Sort indices in descending order
        eigvecs_sorted = eigvecs[:, sorted_indices]

        # Calculate noise subspace
        noise_subspace = eigvecs_sorted[:, self.num_sources:]  # Select the smallest eigenvectors

        # Compute the spatial spectrum
        music_spectrum = 1 / np.sum(np.abs(self.steering_matrix.matrix.conj().T @ noise_subspace) ** 2, axis=1)
        # Normalize and return results
        music_spectrum /= np.max(music_spectrum)

        # Put data
        self.port_put(music_spectrum)