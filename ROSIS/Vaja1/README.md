# Audio Signal Analysis

This program records and analyzes various audio signals including vowels, whistling, and the word "erozija" at different pitches and speeds.

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure your microphone is properly connected and configured.

## Usage

Run the main script:
```bash
python main.py
```

The program will:
1. Record vowels 'a', 'i', 'o' at two different pitches
2. Record whistling at two different pitches
3. Record the word "erozija" at two different speeds
4. Generate plots for all recordings
5. Perform cross-correlation analysis between individual vowels and their occurrences in "erozija"

All plots will be saved in the `plots` directory.

## Output

The program generates the following plots:
- Full signal and zoomed view (3-4 periods) for each recording
- Cross-correlation plots for each vowel in both speeds of "erozija"

## Notes

- Each recording is 3 seconds long
- Sample rate is set to 44.1 kHz
- Make sure to record in a quiet environment for best results
- For whistling, be aware of potential noise cancellation effects 