import numpy as np
from Management import pipeline


class Beamform(pipeline.Stage):
    """
    A classical beamformer
    """
    def __init__(self, num_channels, spacing, test_angles=1000, queue_size=4, destinations=None):
        """
        Initialise the beamformer
        :param num_channels: The number of microphones in the array
        :param spacing: The spacing between microphones in wavelengths
        :param test_angles: The number of angles to test for
        :param queue_size: The size of the input queue
        :param destinations: Where to push results. Object should inherit from Stage
        """
        super().__init__(1, queue_size, destinations)
        self.spacing = spacing
        self.test_angles = test_angles
        self.num_channels = num_channels

        # Pre-compute
        self.theta_scan = None
        self.steering_matrix = None
        self.precompute()

    def precompute(self):
        """
        Precomputation. Run every time a property changes
        :return: None
        """
        self.theta_scan = np.linspace(-1 * np.pi, np.pi, self.test_angles)
        theta_grid, mic_grid = np.meshgrid(self.theta_scan, np.arange(self.num_channels))
        self.steering_matrix = np.exp(-2j * np.pi * self.spacing * mic_grid * np.sin(theta_grid))

    def run(self):
        """
        Runs the beamformer on input data. Ran by a process
        :return: None
        """
        while True:
            # Beamformer
            data = self.input_queue_get()[0]
            r_weighted = np.abs(self.steering_matrix.conj().T @ data.T) ** 2  # Beamforming output

            # Normalize results
            results = 10 * np.log10(np.var(r_weighted, axis=1))  # Power in signal, in dB
            results -= np.max(results)

            # Push X and Y data
            self.destination_queue_put(results)


class MUSIC(pipeline.Stage):
    """
    Implements the MUSIC (MUltiple SIgnal Classification) algorithm
    """
    def __init__(self, num_channels, num_sources, spacing=0.5, test_angles=1000, queue_size=4, destinations=None):
        """
        Initializes the MUSIC
        :param num_channels: The number of microphones from the input data
        :param num_sources: The number of sources in the environment. Cannot be larger than num_channels - 1
        :param spacing: The spacing between microphones in wavelengths
        :param test_angles: The number of angles to test for
        :param queue_size: The size of the input queue
        :param destinations: Where to push output data. Object should inherit Stage
        """
        super().__init__(1, queue_size, destinations)
        self.spacing = spacing
        self.test_angles = test_angles
        self.num_channels = num_channels
        self.num_sources = num_sources

        # Pre-compute
        self.theta_scan = np.linspace(-np.pi / 2, np.pi / 2, self.test_angles)
        self.steering_matrix = np.exp(
            -2j * np.pi * self.spacing * np.arange(self.num_channels)[:, np.newaxis] * np.sin(self.theta_scan))
        self.precompute()

    def precompute(self):
        """
        Pre-computation. Run every time a property changes
        :return: None
        """
        # Steering matrix
        self.theta_scan = np.linspace(-np.pi / 2, np.pi / 2, self.test_angles)
        self.steering_matrix = np.exp(
            -2j * np.pi * self.spacing * np.arange(self.num_channels)[:, np.newaxis] * np.sin(self.theta_scan))

    def run(self):
        """
        Runs MUSIC on input data. Ran by a process
        :return: None
        """
        while True:
            # Calculate the covariance matrix
            data = self.input_queue_get()[0]
            Rx = np.cov(data.T)

            # Decompose into eigenvalues and vectors
            eigvals, eigvecs = np.linalg.eigh(Rx)

            # Sort eigenvalues and corresponding eigenvectors
            sorted_indices = np.argsort(eigvals)[::-1]  # Sort indices in descending order
            eigvecs_sorted = eigvecs[:, sorted_indices]

            # Calculate noise subspace
            noise_subspace = eigvecs_sorted[:, self.num_sources:]  # Select the smallest eigenvectors

            # Compute the spatial spectrum
            music_spectrum = 1 / np.sum(np.abs(self.steering_matrix.conj().T @ noise_subspace) ** 2, axis=1)

            # Normalize and return results
            music_spectrum /= np.max(music_spectrum)

            # Put X and Y data
            self.destination_queue_put(music_spectrum)
