import numpy as np
import multiprocessing as mp
from Management.pipeline import Process


class Beamform(Process):
    def __init__(self, spacing=0.5, test_angles=1000, num_mics=6, queue_size=4):
        # Properties
        super().__init__(queue_size)
        self.spacing = spacing
        self.test_angles = test_angles
        self.num_mics = num_mics

        # Pre-compute
        self.theta_scan = None
        self.steering_matrix = None
        self.precompute()

        # Process
        self.process = mp.Process(target=self._process)
        self.process.start()

    def precompute(self):
        self.theta_scan = np.linspace(-1 * np.pi, np.pi, self.test_angles)
        theta_grid, mic_grid = np.meshgrid(self.theta_scan, np.arange(self.num_mics))
        self.steering_matrix = np.exp(-2j * np.pi * self.spacing * mic_grid * np.sin(theta_grid))

    def _process(self):
        while True:
            # Beamformer
            data = self.in_queue_get()
            r_weighted = np.abs(self.steering_matrix.conj().T @ data.T) ** 2  # Beamforming output

            # Normalize results
            results = 10 * np.log10(np.var(r_weighted, axis=1))  # Power in signal, in dB
            results -= np.max(results)
            self.out_queue_put(results)


class MUSIC(Process):
    def __init__(self, spacing=0.5, test_angles=1000, num_mics=6, num_sources=1, queue_size=4):
        # Properties
        super().__init__(queue_size)
        self.spacing = spacing
        self.test_angles = test_angles
        self.num_mics = num_mics
        self.num_sources = num_sources

        # Pre-compute
        self.theta_scan = np.linspace(-np.pi / 2, np.pi / 2, self.test_angles)
        self.steering_matrix = np.exp(
            -2j * np.pi * self.spacing * np.arange(self.num_mics)[:, np.newaxis] * np.sin(self.theta_scan))
        self.precompute()

        # Process
        self.process = mp.Process(target=self._process)
        self.process.start()


    def precompute(self):
        # Steering matrix
        self.theta_scan = np.linspace(-np.pi / 2, np.pi / 2, self.test_angles)
        self.steering_matrix = np.exp(
            -2j * np.pi * self.spacing * np.arange(self.num_mics)[:, np.newaxis] * np.sin(self.theta_scan))

    def _process(self):
        while True:
            # Calculate the covariance matrix
            data = self.in_queue_get()
            Rx = np.cov(data.T)

            # Decompose into eigenvalues and vectors
            eigvals, eigvecs = np.linalg.eig(Rx)

            # Sort eigenvalues and corresponding eigenvectors
            sorted_indices = np.argsort(eigvals)[::-1]  # Sort indices in descending order
            eigvals_sorted = eigvals[sorted_indices]
            eigvecs_sorted = eigvecs[:, sorted_indices]

            # Calculate noise subspace
            noise_subspace = eigvecs_sorted[:, self.num_sources:]  # Select the smallest eigenvectors

            # Compute the spatial spectrum
            music_spectrum = 1 / np.sum(np.abs(self.steering_matrix.conj().T @ noise_subspace) ** 2, axis=1)

            # Normalize and return results
            music_spectrum /= np.max(music_spectrum)
            self.out_queue_put(music_spectrum)
