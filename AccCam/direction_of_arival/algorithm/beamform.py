import numpy as np
from AccCam.direction_of_arival.geometry import SteeringMatrix


def delay_sum_beamformer(data: np.array, steering_matrix: SteeringMatrix) -> np.array:
    """
    Implements a delay-and-sum (conventional) beamformer
    :param data: The source data to perform the algorithm on
    :param steering_matrix: The steering matrix to utilize to find the sources
    """
    beamformed_data = (steering_matrix.matrix.conj().T @ data.T).real

    # No need for normalization in delay-and-sum beamformer
    return beamformed_data


def bartlett_beamformer(data: np.array, steering_matrix: SteeringMatrix) -> np.array:
    """
    Implements a bartlett beamformer
    :param data: The source data to perform the algorithm on
    :param steering_matrix: The steering matrix to utilize to find the sources
    """
    bartlett_window = np.bartlett(data.shape[0])
    weighted_data = data * bartlett_window[:, None]
    beamformed_data = (steering_matrix.matrix.conj().T @ weighted_data.T).real

    # Normalize
    beamformed_data /= np.max(beamformed_data)
    return beamformed_data


def mvdr_beamformer(data: np.array, steering_matrix: SteeringMatrix) -> np.array:
    """
    Implements a MVDR beamformer
    :param data: The source data to perform the algorithm on
    :param steering_matrix: The steering matrix to utilize to find the sources
    """
    cov_matrix = np.cov(data.T)
    cov_matrix_inv = np.linalg.inv(cov_matrix)
    weights = cov_matrix_inv @ steering_matrix.matrix
    beamformed_data = 1 / np.sum(steering_matrix.matrix.conj().T * weights.T, axis=1).real

    # Normalize
    beamformed_data /= np.max(beamformed_data)
    return beamformed_data


def msnr_beamformer(data: np.array, steering_matrix: SteeringMatrix, noise_covariance: np.array) -> np.array:
    """
    Implements a maximum signal-to-noise ratio (MSNR) beamformer
    :param data: The source data to perform the algorithm on
    :param steering_matrix: The steering matrix to utilize to find the sources
    :param noise_covariance: The covariance matrix of the noise
    """
    noise_cov_inv = np.linalg.inv(noise_covariance)
    weights = noise_cov_inv @ steering_matrix.matrix
    beamformed_data = np.sum(steering_matrix.matrix.conj().T * weights.T, axis=1).real

    # Normalize
    beamformed_data /= np.max(beamformed_data)
    return beamformed_data


def lcmv_beamformer(data: np.array, steering_matrix: SteeringMatrix, constraints: np.array) -> np.array:
    """
    Implements a linearly constrained minimum variance (LCMV) beamformer
    :param data: The source data to perform the algorithm on
    :param steering_matrix: The steering matrix to utilize to find the sources
    :param constraints: The linear constraints on the beamformer response
    """
    constraints_inv = np.linalg.inv(constraints)
    weights = constraints_inv @ steering_matrix.matrix
    beamformed_data = np.sum(steering_matrix.matrix.conj().T * weights.T, axis=1).real

    # Normalize
    beamformed_data /= np.max(beamformed_data)
    return beamformed_data
