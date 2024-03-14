import cupy as np
from Management import pipeline


class MicrophoneArray:
    def __init__(self, positions):



class Beamform(pipeline.Stage):
    """
    Applies beamforming to input data
    """
    def __init__(self, spacing=0.5, test_angles=1000, num_mics=6, queue_size=4, destinations=None):
        """
        Initialise the beamformer
        :param spacing: The spacing of microphones in units of wavelength
        :param test_angles: The number of angles to test for
        :param num_mics: The number of microphones on the axis
        :param queue_size: How many blocks of data to hold in the input queue
        :param destinations: Tuple of destinations to push filtered signals to
        """
        # Properties
        super().__init__(1, queue_size, destinations)
        self.spacing = spacing
        self.test_angles = test_angles
        self.num_mics = num_mics

        # Pre-compute
        self.theta_scan = None
        self.steering_matrix = None
        self.precompute()

    def precompute(self):
        """
        Run whenever properties change
        :return: None
        """
        self.theta_scan = np.linspace(-1 * np.pi, np.pi, self.test_angles)
        theta_grid, mic_grid = np.meshgrid(self.theta_scan, np.arange(self.num_mics))
        self.steering_matrix = np.exp(-2j * np.pi * self.spacing * mic_grid * np.sin(theta_grid))

    def run(self):
        """
        The process. Runs forever, filtering any data in the input queue and pushes results to destinations
        :return: None
        """
        while True:
            # Beamformer
            data = self.input_queue_get()[0]
            r_weighted = np.abs(self.steering_matrix.conj().T @ data.T) ** 2  # Beamforming output

            # Normalize results
            results = 10 * np.log10(np.var(r_weighted, axis=1))  # Power in signal, in dB
            results -= np.max(results)

            self.destination_queue_put(results)


class MUSIC(pipeline.Stage):
    """
    Applies MUSIC (MUltiple SIgnal Classification) to input data
    """
    def __init__(self, spacing=0.5, test_angles=1000, num_mics=6, num_sources=1, queue_size=4, destinations=None):
        """
        Initializes the MUSIC
        :param spacing: The spacing of microphones in units of wavelength
        :param test_angles: The number of angles to test for
        :param num_mics: The number of microphones on the axis
        :param num_sources: The number of audio sources. Cannot be bigger than num_mics - 1
        :param queue_size: How many blocks of data to hold in the input queue
        :param destinations: Tuple of destinations to push filtered signals to
        """
        # Properties
        super().__init__(1, queue_size, destinations)
        self.spacing = spacing
        self.test_angles = test_angles
        self.num_mics = num_mics
        self.num_sources = num_sources

        # Pre-compute
        self.theta_scan = np.linspace(-np.pi / 2, np.pi / 2, self.test_angles)
        self.steering_matrix = np.exp(
            -2j * np.pi * self.spacing * np.arange(self.num_mics)[:, np.newaxis] * np.sin(self.theta_scan))
        self.precompute()


    def precompute(self):
        """
        Run whenever properties change
        :return: None
        """
        # Steering matrix
        self.theta_scan = np.linspace(-np.pi / 2, np.pi / 2, self.test_angles)
        self.steering_matrix = np.exp(
            -2j * np.pi * self.spacing * np.arange(self.num_mics)[:, np.newaxis] * np.sin(self.theta_scan))

    def run(self):
        """
        The process. Runs forever, filtering any data in the input queue and pushes results to destinations
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

            self.destination_queue_put(music_spectrum)
