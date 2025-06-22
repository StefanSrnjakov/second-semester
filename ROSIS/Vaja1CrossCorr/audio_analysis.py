import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
import sounddevice as sd
from scipy.signal import correlate


def record_audio(duration=3, sample_rate=44100):
    print(f"Recording for {duration} seconds...")
    audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
    sd.wait()
    print("Recording finished")

    # Normalize
    audio_data = audio_data.flatten()
    audio_data = audio_data / np.max(np.abs(audio_data))


    return audio_data, sample_rate


def estimate_period_autocorr(signal, sample_rate, max_freq=1000):
    signal = signal - np.mean(signal)  # Remove DC offset
    corr = np.correlate(signal, signal, mode='full')
    corr = corr[len(corr)//2:]  # Keep only positive lags

    # Ignore the zero-lag peak and restrict to max expected frequency
    min_lag = int(sample_rate / max_freq)
    corr[:min_lag] = 0

    peak_lag = np.argmax(corr)
    if peak_lag == 0:
        return None
    return peak_lag / sample_rate  # period in seconds

def plot_audio_signal(audio_data, sample_rate, title="Audio Signal"):
    time = np.arange(len(audio_data)) / sample_rate
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
    
    # Plot full signal
    ax1.plot(time, audio_data)
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Amplitude')
    ax1.set_title(f'{title} - Full Signal')
    ax1.grid(True)

    # Estimate period using autocorrelation
    period = estimate_period_autocorr(audio_data, sample_rate)
    
    if period is not None:
        zoom_duration = period * 4
        zoom_samples = int(zoom_duration * sample_rate)

        # Center zoom on max amplitude
        max_idx = np.argmax(np.abs(audio_data))
        start_idx = max(0, max_idx - zoom_samples // 2)
        end_idx = min(len(audio_data), start_idx + zoom_samples)

        # Adjust if at end of signal
        if end_idx - start_idx < zoom_samples:
            start_idx = max(0, end_idx - zoom_samples)

        ax2.plot(time[start_idx:end_idx], audio_data[start_idx:end_idx])
        ax2.set_xlabel('Time (s)')
        ax2.set_ylabel('Amplitude')
        ax2.set_title(f'{title} - Zoomed View (~4 periods)')
        ax2.grid(True)
    else:
        ax2.set_title('Zoomed View - Period not detected')
        ax2.axis('off')

    plt.tight_layout()
    return fig

def trim_signal(audio_data, sample_rate, target_duration, threshold_ratio=0.02):
    energy = np.abs(audio_data)
    threshold = threshold_ratio * np.max(energy)
    mask = energy > threshold

    if not np.any(mask):
        return np.zeros(int(target_duration * sample_rate))  # silence if no signal detected

    start = np.argmax(mask)
    end = len(audio_data) - np.argmax(mask[::-1])
    trimmed = audio_data[start:end]

    target_samples = int(target_duration * sample_rate)

    if len(trimmed) > target_samples:
        return trimmed[:target_samples]
    elif len(trimmed) < target_samples:
        # pad with zeros
        padding = target_samples - len(trimmed)
        return np.pad(trimmed, (0, padding), mode='constant')
    return trimmed


def trim_silence(signal, threshold=0.01, sample_rate=16000, padding=0.05):
    abs_signal = np.abs(signal)
    above_thresh = np.where(abs_signal > threshold)[0]
    
    if above_thresh.size == 0:
        return signal  # No speech found

    start = max(above_thresh[0] - int(padding * sample_rate), 0)
    end = min(above_thresh[-1] + int(padding * sample_rate), len(signal))
    
    return signal[start:end]


def create_vowel_template(vowel, sample_rate, duration=0.5):
    frequency_map = {'a': 700, 'i': 2300, 'o': 500}
    frequency = frequency_map.get(vowel)
    if frequency is None:
        raise ValueError(f"Vowel '{vowel}' not supported.")
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    template = np.sin(2 * np.pi * frequency * t)
    return template

def find_best_match_segment(signal, template, sample_rate):
    template = (template - np.mean(template)) / np.std(template)
    signal_norm = (signal - np.mean(signal)) / np.std(signal)

    correlation = correlate(signal_norm, template, mode='valid')
    correlation /= len(template)  # normalize by length of the template

    best_index = np.argmax(correlation)
    best_score = correlation[best_index]

    best_start_time = best_index / sample_rate
    best_end_time = (best_index + len(template)) / sample_rate

    return best_start_time, best_end_time, best_score, correlation