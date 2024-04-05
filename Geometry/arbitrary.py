import numpy as np
from functools import cached_property


class Element:
    """
    Defines a point in space where an element lays in distance from origin. Units are wavelengths
    """

    def __init__(self, pos: float):
        self.pos = pos


class SteeringVector:
    """
    Defines a steering vector based on the position of elements
    """

    def __init__(self, elements: tuple, spacing: float):
        self.elements = elements
        self.spacing = spacing

    @cached_property
    def vector(self):
        """
        Calculates the steering vector based on element positions and spacing.
        """
        raise NotImplementedError


class SteeringMatrix:
    """
    Defines a steering matrix based on steering vectors and scanning angles
    """

    def __init__(self, steering_vectors: list, angles: tuple):
        self.steering_vectors = steering_vectors
        self.angles = angles
        self.matrix = np.vstack([sv.vector for sv in self.steering_vectors])


