import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
from scipy import signal
import librosa
import librosa.display

def record_audio(duration=3, sample_rate=44100):
    """
    Record audio for a specified duration.
    
    Args:
        duration (float): Recording duration in seconds
        sample_rate (int): Sample rate in Hz
        
    Returns:
        tuple: (audio_data, sample_rate)
    """
    print(f"Recording for {duration} seconds...")
    audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
    sd.wait()
    print("Recording finished")
    return audio_data.flatten(), sample_rate





def trim_signal(audio_data, sample_rate, target_duration):
    """
    Trim a signal to a target duration.
    
    Args:
        audio_data (numpy.ndarray): Audio signal data
        sample_rate (int): Sample rate in Hz
        target_duration (float): Target duration in seconds
        
    Returns:
        numpy.ndarray: Trimmed audio signal
    """
    target_samples = int(target_duration * sample_rate)
    if len(audio_data) > target_samples:
        return audio_data[:target_samples]
    return audio_data 