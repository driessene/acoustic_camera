class SteeringMatrix:



"""
Beamformer

        self.theta_scan = np.linspace(-1 * np.pi, np.pi, self.test_angles)
        theta_grid, mic_grid = np.meshgrid(self.theta_scan, np.arange(self.num_mics))
        self.steering_matrix = np.exp(-2j * np.pi * self.spacing * mic_grid * np.sin(theta_grid))

MUSIC

        self.theta_scan = np.linspace(-np.pi / 2, np.pi / 2, self.test_angles)
        self.steering_matrix = np.exp(
            -2j * np.pi * self.spacing * np.arange(self.num_mics)[:, np.newaxis] * np.sin(self.theta_scan))
"""