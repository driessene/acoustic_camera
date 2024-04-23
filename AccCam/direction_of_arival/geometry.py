import numpy as np
from dataclasses import dataclass
from functools import cached_property
import matplotlib.pyplot as plt
import logging

logger = logging.getLogger(__name__)

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
    samplerate: int

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


def calculate_steering_vector(elements: list[Element], wavevector: WaveVector):
    """
    Calculates a steering vector based on the position of elements. A steering vector defines how a signal changes based
    on the positions of elements and the given wavevector.
    :param elements: The elements which to calculate the vector for
    :param wavevector: The wavevector to project onto the elements
    """
    # Get positions of elements
    positions = np.array([element.position for element in elements])

    # Algorithm for steering vector: e^(j * (pos . k))
    return np.exp(1j * (positions @ wavevector.k))


class Structure:
    """
    Defines a strucutre made of Elements. Computes its associated steering matrix and other properties.
    """
    def __init__(self,
                 elements: list[Element],
                 wavenumber: float,
                 snr: float,
                 blocksize: int,
                 inclination_range: tuple[float, float] = (0, np.pi),
                 azimuth_range: tuple[float, float] = (0, 2 * np.pi),
                 inclination_resolution: int = 500,
                 azimuth_resolution: int = 500,
                 ):
        """
        :param elements: The elements in the structure. Index must match that of the recorder the structure is linked to.
        :param wavenumber: The ideal and expected wavenumber of the structure to detect.
        :param inclination_range: The inclinations to scan. Default is (0, pi)
        :param azimuth_range: The azimuths to scan. Default is (0, 2pi)
        :param inclination_resolution: The number of angles to scan for on the inclination axis. Default is 500.
        :param azimuth_resolution: The number of angles to scan for on the azimuth axis. Default is 500.
        """
        # Physical properties
        self.elements = elements

        # Signal properties
        self.wavenumber = wavenumber
        self.snr = snr
        self.blocksize = blocksize

        # steering matrix properties
        self.inclination_range = inclination_range
        self.azimuth_range = azimuth_range
        self.inclination_resolution = inclination_resolution
        self.azimuth_resolution = azimuth_resolution

    @cached_property
    def samplerate(self):
        samplerate = self.elements[0].samplerate
        for i, elem in enumerate(self.elements):
            if elem.samplerate != samplerate:
                logger.warning(f"Sampling rate of element {i} does not match sampling rate of the first element "
                               f"(master element)")
        return samplerate


    @cached_property
    def inclination_values(self):
        return np.linspace(*self.inclination_range, self.inclination_resolution)

    @cached_property
    def azimuths_values(self):
        return np.linspace(*self.azimuth_range, self.azimuth_resolution)

    @cached_property
    def steering_matrix(self):
        # Create 3D grid of inclination and azimuth. This gives every combination of angles on a grid
        inclinations_mesh, azimuths_mesh = np.meshgrid(self.inclination_values, self.azimuths_values)

        # Convert inclination and azimuth to spherical coordinates
        spherical_coords = np.array([self.wavenumber * np.ones_like(inclinations_mesh.ravel()),  # Wave number
                                     inclinations_mesh.ravel(),                                  # inclination
                                     azimuths_mesh.ravel()]).T                                   # azimuth

        # Convert spherical coordinates to wave vectors for each set of angles
        wave_vectors = [WaveVector(spherical_to_cartesian(coord), 1) for coord in spherical_coords]

        # Calculate steering vectors for all elements and all set of angles
        steering_vectors = np.array([calculate_steering_vector(self.elements, wave_vector) for wave_vector in wave_vectors]).T

        # Reshape the 3d matrix to 2d for DoA algorithms
        return steering_vectors.reshape(len(self.elements), self.inclination_resolution * self.azimuth_resolution)

    def simulate_audio(self, wavevectors: list[WaveVector], random_phase: bool = True) -> np.ndarray:
        # Randomize phase
        phase = 0
        if random_phase:
            phase = np.random.uniform(-np.pi, np.pi)

        # Time vector as wave propagates
        time_vector = np.arange(self.blocksize) / self.samplerate

        # Individual signals
        frequencies = [wave_vector.angular_frequency for wave_vector in wavevectors]
        waveforms = np.array([np.exp(1j * freq * time_vector + phase) for freq in frequencies])
        steering_vectors = np.array([calculate_steering_vector(self.elements, wave_vector) for wave_vector in wavevectors])

        # Apply wave vectors and sum signals to each element
        signal_matrix = np.sum(np.array([np.outer(sig, vector) for (sig, vector) in zip(waveforms, steering_vectors)]), axis=0).real

        # Generate noise
        signal_power = np.mean(np.abs(signal_matrix) ** 2)
        noise_power = 10 ** ((10 * np.log10(signal_power) - self.snr) / 20)
        noise = np.random.normal(0, np.sqrt(noise_power), (self.blocksize, len(self.elements)))

        # Add noise and normalize
        signal_matrix += noise
        signal_matrix /= np.max(np.abs(signal_matrix))

        return signal_matrix

    def visualize(self):
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')

        positions = np.array([element.position for element in self.elements])
        xs, ys, zs = positions[:, 0], positions[:, 1], positions[:, 2]
        ax.scatter(xs, ys, zs)

        ax.set_title('Element Positions')
        ax.set_xlabel('X pos * wavenumber')
        ax.set_ylabel('Y pos * wavenumber')
        ax.set_zlabel('Z pos * wavenumber')

        plt.show()
