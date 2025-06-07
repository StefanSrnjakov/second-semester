import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.fft import fft, fftfreq

def load_audio(path):
    rate, data = wavfile.read(path)
    if data.ndim > 1:
        data = data[:, 0]  # use one channel if stereo
    return rate, data.astype(float)

def trim_signal(signal, sample_rate, duration=0.5):
    return signal[:int(sample_rate * duration)]

def plot_spectrum(freqs, magnitudes, title, filename):
    plt.figure(figsize=(10, 4))
    plt.plot(freqs, magnitudes)
    plt.title(title)
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude')
    plt.grid(True)
    plt.xlim(0, max(freqs))
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

def compute_fft(signal, sample_rate):
    N = len(signal)
    fft_vals = fft(signal)
    freqs = fftfreq(N, 1/sample_rate)
    return freqs[:N//2], np.abs(fft_vals[:N//2])
