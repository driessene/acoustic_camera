import numpy as np
from Management import Stage, Message


class Beamformer(Stage):
    """
    Implements a basic beamformer
    """

    def __init__(self, steering_matrix, port_size=4, destinations=None):
        """
        :param steering_matrix: The steering matrix for the beamformer
        :param port_size: The size of the input queue
        :param destinations: Where to push output data. Object should inherit Stage
        """
        super().__init__(1, port_size, destinations)
        self.steering_matrix = steering_matrix

    def run(self):
        """
        Runs the beamformer on input data. Ran by a process
        :return: None
        """
        # Get input data
        data = self.port_get()[0].payload

        # Apply beamforming
        beamformed_data = self.steering_matrix.matrix.T.conj() @ data.T

        # Normalize and return results
        beamformed_data /= np.max(beamformed_data)

        # Put data
        self.port_put(Message(beamformed_data))


class MUSIC(Stage):
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
        data = self.port_get()[0].payload
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
        self.port_put(Message(music_spectrum))


# WIP
class SAMV(Stage):
    """
    Implements the SAMV (Spatially Adaptive Multivariate) algorithm
    """
    def __init__(self, steering_matrix, num_sources, port_size=4, destinations=None):
        """
        :param steering_matrix: The steering matrix for the array
        :param num_sources: The number of sources in the environment
        :param port_size: The size of the input queue
        :param destinations: Where to push output data. Object should inherit Stage
        """
        super().__init__(1, port_size, destinations)
        self.steering_matrix = steering_matrix
        self.num_sources = num_sources

    def run(self):
        """
        Runs SAMV on input data. Ran by a process
        :return: None
        """
        # Calculate the covariance matrix
        data = self.port_get()[0].payload()
        Rx = np.cov(data.T)

        # Decompose into eigenvalues and vectors
        eigvals, eigvecs = np.linalg.eigh(Rx)

        # Sort eigenvalues and corresponding eigenvectors
        sorted_indices = np.argsort(eigvals)[::-1]
        eigvecs_sorted = eigvecs[:, sorted_indices]

        # Calculate the spatial spectrum
        samv_spectrum = np.zeros(self.steering_matrix.matrix.shape[1])
        for i in range(self.steering_matrix.matrix.shape[1]):
            W = self.steering_matrix.matrix[:, :i+1]
            M = np.dot(W, W.conj().T)
            samv_spectrum[i] = np.trace(np.dot(M, Rx))

        # Normalize and return results
        samv_spectrum /= np.max(samv_spectrum)

        # Put data
        self.port_put(Message(samv_spectrum))
