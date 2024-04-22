import numpy as np
from ..geometry import SteeringMatrix


def music(data: np.array, steering_matrix: SteeringMatrix, num_sources: int) -> np.array:
    """
    Implements the MUSIC (MUltiple SIgnal Classification) algorithm
    :param data: The source data to preform the algorithm on
    :param steering_matrix: The steering matrix to utilize to find the sources
    :param num_sources: The number of sources to find.
    """
    # Calculate the covariance matrix

    Rx = np.cov(data.T)

    # Decompose into eigenvalues and vectors
    eigvals, eigvecs = np.linalg.eigh(Rx)

    # step 1 - Sort eigenvalues and corresponding eigenvectors from smallest to largest
    # step 2 - Take the smallest as the Noise subspace.
    noise_subspace = eigvecs[:, np.argsort(eigvals)[::-1]][:, num_sources:]

    # Compute the music spectrum. Use np.sum to take several samples into one result
    music_spectrum = 1 / np.sum(np.abs(np.dot(steering_matrix.matrix.conj().T, noise_subspace)) ** 2, axis=1)

    # Normalize and return results
    music_spectrum /= np.max(music_spectrum)
    return music_spectrum
