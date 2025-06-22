import numpy as np

def real_scalar_product(signal, sample_rate, freqs):
    n = np.arange(len(signal))
    result = []

    for f in freqs:
        cos = np.cos(2 * np.pi * f * n / sample_rate)
        real_proj = np.dot(signal, cos)
        result.append(np.abs(real_proj))
    
    return np.array(result)


def complex_scalar_product(signal, sample_rate, freqs):
    n = np.arange(len(signal))
    result = []

    for f in freqs:
        sin = np.sin(2 * np.pi * f * n / sample_rate)
        cos = np.cos(2 * np.pi * f * n / sample_rate)
        real_proj = np.dot(signal, cos)
        imag_proj = np.dot(signal, sin)
        magnitude = np.sqrt(real_proj**2 + imag_proj**2)
        result.append(magnitude)
    
    return np.array(result)
