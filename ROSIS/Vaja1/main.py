import numpy as np
import matplotlib.pyplot as plt
from audio_analysis import record_audio, plot_audio_signal, cross_correlate, trim_signal
import os

def save_plot(fig, filename):
    """Save plot to file"""
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close(fig)

def main():
    # Create output directory for plots
    os.makedirs('plots', exist_ok=True)
    
    # Recording parameters
    duration = 3  # seconds
    sample_rate = 44100
    
    # Dictionary to store all recordings
    recordings = {}
    
    # Record vowels 'a', 'i', 'o' at two different pitches
    vowels = ['a', 'i', 'o']
    for vowel in vowels:
        print(f"\nRecording vowel '{vowel}' at first pitch...")
        recordings[f'{vowel}_1'], _ = record_audio(duration, sample_rate)
        
        print(f"\nRecording vowel '{vowel}' at second pitch...")
        recordings[f'{vowel}_2'], _ = record_audio(duration, sample_rate)
    
    # Record whistling at two different pitches
    print("\nRecording whistling at first pitch...")
    recordings['whistle_1'], _ = record_audio(duration, sample_rate)
    
    print("\nRecording whistling at second pitch...")
    recordings['whistle_2'], _ = record_audio(duration, sample_rate)
    
    # Record word "erozija" at two different speeds
    print("\nRecording word 'erozija' at first speed...")
    recordings['erozija_1'], _ = record_audio(duration, sample_rate)
    
    print("\nRecording word 'erozija' at second speed...")
    recordings['erozija_2'], _ = record_audio(duration, sample_rate)
    
    # Plot all recordings
    for name, data in recordings.items():
        fig = plot_audio_signal(data, sample_rate, title=f"Signal: {name}")
        save_plot(fig, f'plots/{name}.png')
    
    # Cross-correlation analysis
    print("\nPerforming cross-correlation analysis...")
    
    # Estimate vowel durations in "erozija" (approximately 0.2 seconds each)
    vowel_duration = 0.2
    
    # Trim vowel recordings to match estimated duration in "erozija"
    trimmed_vowels = {}
    for vowel in vowels:
        trimmed_vowels[vowel] = trim_signal(recordings[f'{vowel}_1'], sample_rate, vowel_duration)
    
    # Perform cross-correlation for each vowel in both "erozija" recordings
    for speed in ['1', '2']:
        erozija = recordings[f'erozija_{speed}']
        
        for vowel in vowels:
            correlation = cross_correlate(erozija, trimmed_vowels[vowel])
            time = np.arange(len(correlation)) / sample_rate
            
            plt.figure(figsize=(12, 4))
            plt.plot(time, correlation)
            plt.title(f'Cross-correlation: vowel "{vowel}" in "erozija" (speed {speed})')
            plt.xlabel('Time (s)')
            plt.ylabel('Correlation')
            plt.grid(True)
            save_plot(plt.gcf(), f'plots/correlation_{vowel}_speed{speed}.png')
    
    print("\nAnalysis complete! Check the 'plots' directory for all generated plots.")

if __name__ == "__main__":
    main() 