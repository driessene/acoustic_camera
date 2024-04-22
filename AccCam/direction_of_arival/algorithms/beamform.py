import numpy as np
from ..geometry import SteeringMatrix

def Beamformer(data: np.array, steering_matrix: SteeringMatrix) -> np.array:
    """
    Implements a delay-and-sum (conventional) beamformer
    :param data: The source data to preform the algorithm on
    :param steering_matrix: The steering matrix to utilize to find the sources
    """

    # Apply beamforming, then measure power
    beamformed_data = 10 * np.log10(np.var((steering_matrix.matrix.conj().T @ data.T), axis=1))

    # Normalize
    beamformed_data /= np.max(beamformed_data)
    return beamformed_data
