import numpy as np
from functools import cached_property


class OneDimensionalArray:
    def __init__(self, spacing, num_channels, delta_theta=0.1):
        self.spacing = spacing
        self.num_channels = num_channels
        self.delta_theta = delta_theta

    @cached_property
    def theta_scan(self):
        return np.arange(-np.pi / 2, np.pi / 2, self.delta_theta)

    @cached_property
    def matrix(self):
        return np.exp(-2j * np.pi * self.spacing * np.arange(self.num_channels)[:, np.newaxis] * np.sin(self.theta_scan))
        #      | Euler's formula |
        #                           |                            Radius                       |
        #                                                                                        |       angle         |
