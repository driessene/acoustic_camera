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
    Defines a wave vector. K must be given as np.array([kx, ky, kz]). Provides all properties of the wavevector
    """
    k: np.array  # (kx, ky, kz)
    wave_speed: float   # speed in m/s of the wave in the environment

    @cached_property
    def spherical_k(self):
        # (wavenumber, inclination, azimuth)
        return cartesian_to_spherical(self.k)

    # ANGULAR PROPERTIES

    @cached_property
    def inclination(self):
        return self.spherical_k[1]

    @cached_property
    def azimuth(self):
        return self.spherical_k[2]

    @cached_property
    def angular_wavenumber(self):
        return self.spherical_k[0]

    @cached_property
    def angular_wavelength(self):
        return 1 / self.angular_wavenumber

    @cached_property
    def angular_frequency(self):
        return self.angular_wavenumber * self.wave_speed

    @cached_property
    def angular_period(self):
        return 1 / self.angular_frequency

    # LINEAR PROPERTIES

    @cached_property
    def linear_wavenumber(self):
        return self.angular_wavenumber / (2 * np.pi)

    @cached_property
    def linear_wavelength(self):
        return self.angular_wavelength * (2 * np.pi)

    @cached_property
    def linear_frequency(self):
        return self.angular_frequency / (2 * np.pi)

    @cached_property
    def linear_period(self):
        return self.angular_period * (2 * np.pi)


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
            [np.exp(1j * (element.cartesian_position @ self.wavevector.k))
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
            [SteeringVector(
                self.elements,
                WaveVector(spherical_to_cartesian(np.array([self.wavenumber, inclination, azimuth])), 1)).vector
             for (azimuth, inclination) in product(self.azimuths, self.inclinations)]).T


