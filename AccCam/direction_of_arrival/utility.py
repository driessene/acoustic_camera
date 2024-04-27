def hz_to_cm(linear_frequency: float, wave_speed: float) -> float:
    """
    Useful for converting target hz measurement to ideal element spacing, assuming uniform spacing
    :param linear_frequency: The target hz measurement
    :param wave_speed: The speed of the wave in meters per second
    :return: The ideal distance between elements
    """
    linear_wavelength = wave_speed / linear_frequency
    half_wavelength = linear_wavelength / 2
    half_wavelength_cm = half_wavelength * 100
    return half_wavelength_cm