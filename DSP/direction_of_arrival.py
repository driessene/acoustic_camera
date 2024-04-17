import numpy as np
from Management import Stage, Message


class Beamformer(Stage):
    """
    Implements a delay-and-sum (conventional) beamformer
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
        # Get input data
        data = self.port_get()[0].payload

        # Apply beamforming, then measure power
        beamformed_data = 10 * np.log10(np.var((self.steering_matrix.matrix.conj().T @ data.T), axis=1))

        # Normalize
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
        # Calculate the covariance matrix
        data = self.port_get()[0].payload
        Rx = np.cov(data.T)

        # Decompose into eigenvalues and vectors
        eigvals, eigvecs = np.linalg.eigh(Rx)

        # step 1 - Sort eigenvalues and corresponding eigenvectors from smallest to largest
        # step 2 - Take the smallest as the Noise subspace.
        noise_subspace = eigvecs[:, np.argsort(eigvals)[::-1]][:, self.num_sources:]

        # Compute the music spectrum. Use np.sum to take several samples into one result
        music_spectrum = 1 / np.sum(np.abs(np.dot(self.steering_matrix.matrix.conj().T, noise_subspace)) ** 2, axis=1)

        # Normalize and return results
        music_spectrum /= np.max(music_spectrum)
        self.port_put(Message(music_spectrum))
