import os
import numpy as np
from frequency_analysis import real_scalar_product, complex_scalar_product
from utils import load_audio, trim_signal, plot_spectrum, compute_fft

vowels = ['a', 'i', 'o']
duration = 0.5
N = 5000  # frequency limit

os.makedirs("output", exist_ok=True)

for vowel in vowels:
    print(f"Processing vowel: {vowel}")
    path = f"audio_data/{vowel}_2_trimmed.wav"
    rate, signal = load_audio(path)
    signal = trim_signal(signal, rate, duration)

    # FFT analysis
    fft_freqs, fft_mag = compute_fft(signal, rate)
    # Limit FFT to 5000 Hz
    mask = fft_freqs <= N
    fft_freqs = fft_freqs[mask]
    fft_mag = fft_mag[mask]
    plot_spectrum(fft_freqs, fft_mag, f"{vowel.upper()} - FFT", f"output/{vowel}_fft.png")

    # Use only freqs up to 5000Hz
    freqs = np.linspace(0, min(N, rate/2), 5000)

    # Real sinusoids
    real_mag = real_scalar_product(signal, rate, freqs)
    plot_spectrum(freqs, real_mag, f"{vowel.upper()} - Real Sinusoids", f"output/{vowel}_real.png")

    # Complex sinusoids
    complex_mag = complex_scalar_product(signal, rate, freqs)
    plot_spectrum(freqs, complex_mag, f"{vowel.upper()} - Complex Sinusoids", f"output/{vowel}_complex.png")

    print(f"Graphs saved for {vowel}")
