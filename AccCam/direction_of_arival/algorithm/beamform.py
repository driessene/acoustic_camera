import numpy as np
from AccCam.direction_of_arival.geometry import SteeringMatrix


def delay_sum_beamformer(data: np.array, steering_matrix: SteeringMatrix) -> np.array:
    """
    Implements a delay-and-sum (conventional) beamformer
    :param data: The source data to perform the algorithm on
    :param steering_matrix: The steering matrix to utilize to find the sources
    """
    beamformed_data = np.var(steering_matrix.matrix.conj().T @ data.T, axis=1).real

    # Normalize
    beamformed_data /= np.max(beamformed_data)
    return beamformed_data


def bartlett_beamformer(data: np.array, steering_matrix: SteeringMatrix) -> np.array:
    """
    Implements a bartlett beamformer
    :param data: The source data to perform the algorithm on
    :param steering_matrix: The steering matrix to utilize to find the sources
    """
    cov_matrix = np.cov(data.T)
    beamformed_data = np.sum(steering_matrix.matrix.conj().T * (cov_matrix @ steering_matrix.matrix).T, axis=1).real

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
    beamformed_data = 1 / np.sum(steering_matrix.matrix.conj().T *
                                 np.linalg.lstsq(cov_matrix, steering_matrix.matrix, None)[0].T, axis=1).real

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
    beamformed_data = np.sum(steering_matrix.matrix.conj().T *
                             (noise_cov_inv @ steering_matrix.matrix).T, axis=1).real

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
    beamformed_data = np.sum(steering_matrix.matrix.conj().T *
                             (constraints_inv @ steering_matrix.matrix).T, axis=1).real

    # Normalize
    beamformed_data /= np.max(beamformed_data)
    return beamformed_data
