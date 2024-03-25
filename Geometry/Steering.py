import numpy as np


class Element:
    """
    Defines a point in space where an element lays. Given in cartiesian cordinates where the units are wavelengths
    """

    def __init__(self, pos: tuple):
        self.pos = pos


class SteeringVector:
    """
    Defines a steering vector based on the position of elements
    """

    def __init__(self, elements: tuple, spacing: float):
        self.elements = elements
        self.spacing = spacing

    @property
    def vector(self):
        """
        Calculates the steering vector based on element positions and spacing.
        """
        positions = np.array([element.pos for element in self.elements])  # Convert tuple to NumPy array for calculation
        return np.exp(-2j * np.pi * self.spacing * np.dot(positions, np.arange(len(self.elements))))


class SteeringMatrix:
    """
    Defines a steering matrix based on steering vectors and scanning angles
    """

    def __init__(self, steering_vectors: list, angles: tuple):
        self.steering_vectors = steering_vectors
        self.angles = angles
        self.matrix = np.vstack([sv.vector for sv in self.steering_vectors])


"""
MUSIC
        self.theta_scan = np.linspace(-np.pi / 2, np.pi / 2, self.test_angles)
        self.steering_matrix = np.exp(
            -2j * np.pi * self.spacing * np.arange(self.num_mics)[:, np.newaxis] * np.sin(self.theta_scan))
"""