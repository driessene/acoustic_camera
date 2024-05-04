from AccCam.__config__ import __USE_CUPY__

if __USE_CUPY__:
    import cupy as np
else:
    import numpy as np

from functools import cached_property
import matplotlib.pyplot as plt
import logging

logger = logging.getLogger(__name__)


def spherical_to_cartesian(spherical_pos: np.ndarray):
    # (radius, inclination, azimuth) -> (x, y, z)
    return np.array([
        spherical_pos[0] * np.sin(spherical_pos[1]) * np.cos(spherical_pos[2]),
        spherical_pos[0] * np.sin(spherical_pos[1]) * np.sin(spherical_pos[2]),
        spherical_pos[0] * np.cos(spherical_pos[1])
    ])


def cartesian_to_spherical(cartesian_pos: np.ndarray):
    # (x, y, z) -> (radius, inclination, azimuth)
    r = np.sqrt(np.sum(np.square(cartesian_pos)))
    return np.array([
        r,
        np.arctan(cartesian_pos[1] / cartesian_pos[0]),
        np.arccos(cartesian_pos[2] / r)
    ])


class Element:
    """
    Defines a point in space where an element lays in distance from origin. Units are in wavelengths.
    """
    def __init__(self, position: np.ndarray, samplerate: int):
        """
        :param position: (x, y, z). In units of meters * wavenumber. For example, for a uniformly spaced array, all
            elements are seperated by 0.5 ideally.
        :param samplerate: The samplerate of the element
        """
        self.position = position
        self.samplerate = samplerate

    @cached_property
    def spherical_position(self):
        return cartesian_to_spherical(self.position)


class WaveVector:
    """
    Defines a wave vector. K must be given as np.array([kx, ky, kz]) in units of angular wavenumber.
    Provides all properties of the wavevector as properties.
    """
    def __init__(self, k: np.ndarray, wave_speed: float):
        """
        :param k: The 3-dimensional vector representing the wavevector (kx, ky, kz). Each of these are the angular
            wavenumber in said dimension. If you would like fo give (wavenumber, inclination, azimuth), which is more
            common. use spherical_to_cartesian(np.array([wavenumber, inclination, azimuth]).
        :param wave_speed: The speed of wave propagation in meters per second. Note that the speed of sound in air is
        always 343 meters per second unless extreme air pressures or atmospheres are present.
        """
        self.k = k
        self.wave_speed = wave_speed

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


class Structure:
    """
    Defines a structure made of Elements. Computes its associated steering matrix and other properties.
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
        :param elements: The elements in the structure. Index must match that of the recorder the structure is linked
            to.
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
    def positions(self):
        return np.array([element.position for element in self.elements])

    def steering_vector(self, wavevector: WaveVector):
        """
        Calculates a steering vector based on the structure and a given wave vector.
        :param wavevector: The wavevector to project onto the elements
        :returns: a steering vector which describes the reaction of the elements to the wavevector
        """
        # Algorithm for steering vector: e^(j * (pos . k))
        return np.exp(1j * (self.positions @ wavevector.k))

    @cached_property
    def steering_matrix(self):
        # Create 3D grid of inclination and azimuth. This gives every combination of angles on a grid
        inclinations_mesh, azimuths_mesh = np.meshgrid(self.inclination_values, self.azimuths_values)

        # Convert inclination and azimuth to spherical coordinates
        spherical_coords = np.array([self.wavenumber * np.ones_like(inclinations_mesh.ravel()),  # Wave number
                                     inclinations_mesh.ravel(),                                  # inclination
                                     azimuths_mesh.ravel()]).T                                   # azimuth

        # Convert spherical coordinates to wave vectors for each set of angles. Wave speed does not matter here
        wavevectors = [WaveVector(spherical_to_cartesian(coord), 1) for coord in spherical_coords]

        # Calculate steering vectors for all elements and all set of angles
        steering_vectors = np.array([self.steering_vector(wavevector) for wavevector in wavevectors]).T

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
        steering_vectors = np.array([self.steering_vector(wave_vector) for wave_vector in wavevectors])

        # Apply wave vectors and sum signals to each element
        signal_matrix = np.sum(np.array([np.outer(sig, vector) for (sig, vector) in zip(waveforms, steering_vectors)]),
                               axis=0).real

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

        if __USE_CUPY__:
            xs, ys, zs = xs.get(), ys.get(), zs.get()

        ax.scatter(xs, ys, zs)

        ax.set_title('Element Positions')
        ax.set_xlabel('X pos * wavenumber')
        ax.set_ylabel('Y pos * wavenumber')
        ax.set_zlabel('Z pos * wavenumber')

        plt.show()
