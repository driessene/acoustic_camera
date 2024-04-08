import numpy as np
from functools import cached_property


def spherical_to_cartesian(radius, azimuth, inclination):
    return np.array([
        radius * np.sin(inclination) * np.cos(azimuth),
        radius * np.sin(inclination) * np.sin(azimuth),
        radius * np.cos(inclination)
    ])


class Element:
    """
    Defines a point in space where an element lays in distance from origin. Units are meters.
    """
    def __init__(self, spherical_position):
        """
        :param spherical_position: Array of which (radius, azimuth, elevation)
        """
        # (radius, azimuth, elevation)
        self.spherical_position = spherical_position

    @cached_property
    def cartesian_position(self):
        return spherical_to_cartesian(*self.spherical_position)


class WaveVector:
    def __init__(self, spherical_k, wave_speed):
        """
        :param spherical_k: (wavenumber, azimuth, elevation) of the wave
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
        :param theta: wave vector of the signal
        """
        self.elements = elements
        self.wavevector = wavevector

    @cached_property
    def vector(self):
        vector = []
        for element in self.elements:
            vector.append(
                np.exp(1j * np.dot(
                        element.cartesian_position,
                        (self.wavevector.cartesian_k / (2 * np.pi * self.wavevector.spherical_k[0]))
                    )
                )
            )
        return np.array(vector)


class SteeringMatrix:
    """
    Defines a steering matrix based on the position of elements and thetas for which to test
    """
    def __init__(self, elements: list, azimuths, inclinations, wavenumber, wave_speed):
        """
        :param elements: The elements to include in the vectors
        :param azimuths: The azimuths to include in the vectors
        :param inclinations: The elevations to include in the vectors
        :param wavenumber: The wavenumber to test for
        :param wave_speed: The speed of the wave in m/s
        """
        self.elements = elements
        self.azimuths = azimuths
        self.inclinations = inclinations
        self.wavenumber = wavenumber
        self.wave_speed = wave_speed

    @cached_property
    def matrix(self):
        vectors = []
        for inclination in self.inclinations:
            for azimuth in self.azimuths:
                wave_vector = WaveVector((self.wavenumber, azimuth, inclination), self.wave_speed)
                vectors.append(SteeringVector(self.elements, wave_vector).vector)

        return np.vstack(vectors).T
