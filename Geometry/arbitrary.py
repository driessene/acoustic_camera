import numpy as np
from functools import cached_property
from itertools import product


def spherical_to_cartesian(radius, inclination, azimuth):
    return np.array([
        radius * np.sin(inclination) * np.cos(azimuth),
        radius * np.sin(inclination) * np.sin(azimuth),
        radius * np.cos(inclination)
    ])


def cartesian_to_spherical(x, y, z):
    r = np.sqrt(np.sum(np.square([x, y, z])))
    return np.array([
        r,
        np.arctan(y / x),
        np.arccos(z / r)
    ])


class Element:
    """
    Defines a point in space where an element lays in distance from origin. Units are meters.
    """
    def __init__(self, cartesian_position):
        """
        :param cartesian_position: Array of which (x, y, z)
        """
        # (x, y, z)
        self.cartesian_position = cartesian_position

    @cached_property
    def spherical_position(self):
        return cartesian_to_spherical(*self.cartesian_position)


class WaveVector:
    def __init__(self, spherical_k, wave_speed):
        """
        :param spherical_k: (wavenumber, inclination, azimuth) of the wave
        :param wave_speed: The speed of the wave in meters per second
        """
        self.spherical_k = spherical_k
        self.wave_speed = wave_speed

    @cached_property
    def cartesian_k(self):
        return np.pi * 2 * spherical_to_cartesian(*self.spherical_k)

    @cached_property
    def wavelength(self):
        return 1 / self.spherical_k[0]

    @cached_property
    def frequency(self):
        return self.spherical_k[0] * self.wave_speed


class SteeringVector:
    """
    Defines a steering vector based on the position of elements
    """
    def __init__(self, elements: list, wavevector: WaveVector):
        """
        :param elements: The elements to include in the vector
        :param wavevector: wave-vector of the signal
        """
        self.elements = elements
        self.wavevector = wavevector

    @cached_property
    def vector(self):
        return np.array(
            [np.exp(1j * np.dot(element.cartesian_position, self.wavevector.cartesian_k))
             for element in self.elements])


class SteeringMatrix:
    """
    Defines a steering matrix based on the position of elements and thetas for which to test
    """
    def __init__(self, elements: list, inclinations, azimuths, wavenumber, wave_speed):
        """
        :param elements: The elements to include in the vectors
        :param inclinations: The elevations to include in the vectors
        :param azimuths: The azimuths to include in the vectors
        :param wavenumber: The wave-number to test for
        :param wave_speed: The speed of the wave in m/s
        """
        self.elements = elements
        self.azimuths = azimuths
        self.inclinations = inclinations
        self.wavenumber = wavenumber
        self.wave_speed = wave_speed

    @cached_property
    def matrix(self):
        return np.vstack(
            [SteeringVector(self.elements, WaveVector((self.wavenumber, azimuth, inclination), self.wave_speed)).vector
             for (inclination, azimuth) in product(self.inclinations, self.azimuths)]).T
