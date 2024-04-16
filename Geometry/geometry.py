import numpy as np
from dataclasses import dataclass
from functools import cached_property
from itertools import product


def spherical_to_cartesian(spherical_pos: np.array):
    # (radius, inclination, azimuth) -> (x, y, z)
    return np.array([
        spherical_pos[0] * np.sin(spherical_pos[1]) * np.cos(spherical_pos[2]),
        spherical_pos[0] * np.sin(spherical_pos[1]) * np.sin(spherical_pos[2]),
        spherical_pos[0] * np.cos(spherical_pos[1])
    ])


def cartesian_to_spherical(cartesian_pos: np.array):
    # (x, y, z) -> (radius, inclination, azimuth)
    r = np.sqrt(np.sum(np.square(cartesian_pos)))
    return np.array([
        r,
        np.arctan(cartesian_pos[1] / cartesian_pos[0]),
        np.arccos(cartesian_pos[2] / r)
    ])


@dataclass
class Element:
    """
    Defines a point in space where an element lays in distance from origin. Units are in wavelengths.
    """
    cartesian_position: np.array   # (x, y, z) position

    @cached_property
    def spherical_position(self):
        return cartesian_to_spherical(self.cartesian_position)


@dataclass
class WaveVector:
    """
    Defines a wave vector.
    """
    spherical_k: np.array  # (wavenumber, inclination, azimuth)
    wave_speed: float   # speed in m/s of the wave in the environment

    @cached_property
    def cartesian_k(self):
        return np.pi * 2 * spherical_to_cartesian(self.spherical_k)

    @cached_property
    def wavelength(self):
        return 1 / self.spherical_k[0]

    @cached_property
    def frequency(self):
        return self.spherical_k[0] * self.wave_speed


@dataclass
class SteeringVector:
    """
    Defines a steering vector based on the position of elements
    """
    elements: list[Element]     # The elements to include in the vector
    wavevector: WaveVector      # wave vector of the signal

    @cached_property
    def vector(self):
        return np.array(
            [np.exp(1j * np.dot(element.cartesian_position, self.wavevector.cartesian_k))
             for element in self.elements])


@dataclass
class SteeringMatrix:
    """
    Defines a steering matrix based on the position of elements and thetas for which to test
    """
    elements: list[Element]     # The elements to include in the vectors
    inclinations: np.array      # The inclinations to include in the matrix
    azimuths: np.array          # The azimuths to include in the matrix
    wavenumber: float           # The wavenumber of the signal

    @cached_property
    def matrix(self):
        return np.vstack(
            [SteeringVector(self.elements, WaveVector((self.wavenumber, inclination, azimuth), 1)).vector
             for (azimuth, inclination) in product(self.azimuths, self.inclinations)]).T
