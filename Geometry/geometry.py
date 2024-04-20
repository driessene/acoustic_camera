import numpy as np
from dataclasses import dataclass
from functools import cached_property


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
    position: np.array   # (x, y, z) position

    @cached_property
    def spherical_position(self):
        return cartesian_to_spherical(self.position)


@dataclass
class WaveVector:
    """
    Defines a wave vector. K must be given as np.array([kx, ky, kz]) in units of angular wavenumber.
    Provides all properties of the wavevector as properties.
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
    Defines a steering vector based on the position of elements. A steering vector defines how a signal changes based
    on the positions of elements and the given wavevector.
    """
    elements: list[Element]     # The elements to include in the vector
    wavevector: WaveVector      # wave vector of the signal

    @cached_property
    def vector(self):
        # Get positions of elements
        positions = np.array([element.position for element in self.elements])

        # Algorithm for steering vector: e^(j * (pos . k))
        return np.exp(1j * (positions @ self.wavevector.k))


@dataclass
class SteeringMatrix:
    """
    Defines a steering matrix based on the position of elements and thetas for which to test. A Steering matrix just
    holds every possible steering vector. Used in DoA algorithms.
    """
    elements: list[Element]     # The elements to include in the vectors
    inclinations: np.array      # The inclinations to include in the matrix
    azimuths: np.array          # The azimuths to include in the matrix
    wavenumber: float           # The wavenumber of the signal

    @cached_property
    def matrix(self):
        # Create 3D grid of inclination and azimuth. This gives every combination of angles on a grid
        inclinations, azimuths = np.meshgrid(self.inclinations, self.azimuths)

        # Convert inclination and azimuth to spherical coordinates
        spherical_coords = np.array([self.wavenumber * np.ones_like(inclinations.ravel()),  # Wave number
                                     inclinations.ravel(),                                  # inclination
                                     azimuths.ravel()]).T                                   # azimuth

        # Convert spherical coordinates to wave vectors for each set of angles
        wave_vectors = [WaveVector(spherical_to_cartesian(coord), 1) for coord in spherical_coords]

        # Calculate steering vectors for all elements and all set of angles
        steering_vectors = np.array([SteeringVector(self.elements, wave_vector).vector for wave_vector in wave_vectors]).T

        # Reshape the 3d matrix to 2d for DoA algorithms
        return steering_vectors.reshape(len(self.elements), len(self.inclinations) * len(self.azimuths))
