import numpy as np
from AccCam.direction_of_arival.geometry import SteeringMatrix


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


def music(data: np.array, steering_matrix: SteeringMatrix, num_sources: int) -> np.array:
    """
    Implements the MUSIC (MUltiple SIgnal Classification) algorithm
    :param data: The source data to preform the algorithm on
    :param steering_matrix: The steering matrix to utilize to find the sources
    :param num_sources: The number of sources to find.
    """
    # Get noise subspace:
    noise_subspace = find_noise_subspace(data, num_sources)

    # Compute the music spectrum. Use np.sum to take several samples into one result
    music_spectrum = 1 / np.sum(np.abs(np.dot(steering_matrix.matrix.conj().T, noise_subspace)) ** 2, axis=1)

    # Normalize and return results
    music_spectrum /= np.max(music_spectrum)
    return music_spectrum

# WIP
def wideband_music(data: np.array, steering_matrix: SteeringMatrix, num_sources: int, wavenumber_range: tuple[float]) \
        -> np.array:
    """
    Implements the MUSIC (MUltiple SIgnal Classification) algorithm on a wide-band signal
    :param data: The source data to preform the algorithm on
    :param steering_matrix: The steering matrix to utilize to find the sources
    :param num_sources: The number of sources to find.
    :param wavenumber_range: The range (min, max) of wavenumbers to include in the band. SteeringMatrix.wavenumber
        should be in the middle of this band.
    """
    # Get noise subspace:
    noise_subspace = find_noise_subspace(data, 1)
    print(noise_subspace.shape)

    # Weigh eigenvalues
    wavenumbers = np.linspace(wavenumber_range[0], wavenumber_range[1], len(steering_matrix.elements))
    weight = np.diag(wavenumbers) / np.sqrt(np.sum(np.square(wavenumbers)))


    # Compute the music spectrum. Use np.sum to take several samples into one result
    music_spectrum = np.sum(
        (steering_matrix.matrix.conj().T @ steering_matrix.matrix) /
        (steering_matrix.matrix.conj().T @ noise_subspace @ weight @ noise_subspace.conj().T @ steering_matrix.matrix),
        axis=1
    )

    # Normalize and return results
    music_spectrum /= np.max(music_spectrum)
    return music_spectrum
