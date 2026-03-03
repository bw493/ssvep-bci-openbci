# SSVEP BCI Data Files

This directory contains EEG data collected using OpenBCI Cyton board.

## Data Collection Details

**Hardware:**
- OpenBCI Cyton Board (8 channels)
- Sampling Rate: 250 Hz
- Electrodes: Cz, C3, C4, CPz, F3, F4, P3, P4

**Recording Sessions:**
1. **2026-02-23 19:05-06** - Initial SSVEP experiment
   - BrainFlow-RAW_2026-02-23_19-05-38_0.csv
   - OpenBCI-RAW-2026-02-23_19-06-24.txt

2. **2026-02-26 19:22** - SSVEP session 2
   - OpenBCI-RAW-2026-02-26_19-22-57.txt

3. **2026-02-26 19:35** - SSVEP session 3
   - OpenBCI-RAW-2026-02-26_19-35-13.txt

## File Formats

### OpenBCI-RAW TXT Format
- Exported from OpenBCI GUI
- Comma-separated values
- Header includes channel information and sampling rate
- Columns: Sample Index, EXG Channels 0-7, Accelerometer, Digital channels, Timestamp

### BrainFlow CSV Format
- Tab-separated values
- Raw format from BrainFlow library
- Columns 1-8: EEG channels
- Column 22: Timestamp

## Data Structure

```
data/
├── raw/                    # Original data files
│   ├── OpenBCI-RAW-2026-02-23_19-06-24.txt
│   ├── OpenBCI-RAW-2026-02-26_19-22-57.txt
│   ├── OpenBCI-RAW-2026-02-26_19-35-13.txt
│   └── BrainFlow-RAW_2026-02-23_19-05-38_0.csv
└── processed/              # Converted FIF files (generated)
    └── *.fif
```

## Converting Data to FIF Format

Use the conversion script to convert raw data to MNE-compatible FIF format:

### Convert all files in raw directory:
```bash
python scripts/convert_openbci_data.py --input-dir data/raw/ --output-dir data/processed/
```

### Convert a single file:
```bash
python scripts/convert_openbci_data.py --input data/raw/OpenBCI-RAW-2026-02-23_19-06-24.txt --output data/processed/session1.fif
```

## Using the Data with the Pipeline

After conversion to FIF format:

```bash
# Run the complete pipeline on a session
python scripts/run_pipeline.py --data data/processed/OpenBCI-RAW-2026-02-23_19-06-24.fif

# Run with real Arduino (not simulation)
python scripts/run_pipeline.py --data data/processed/session1.fif --no-simulation

# Use PSD features instead of CSP
python scripts/run_pipeline.py --data data/processed/session1.fif --no-csp
```

## Data Quality Notes

**Preprocessing Applied:**
- 50 Hz notch filter (power line noise removal)
- 6-40 Hz bandpass filter (SSVEP-relevant frequencies)
- Common Average Reference (CAR)
- ICA for artifact removal

**Expected Artifacts:**
- Eye blinks (typically in frontal channels)
- Muscle activity (high frequency noise)
- Movement artifacts

These are automatically handled by the ICA preprocessing step.

## Data Privacy & Ethics

- All data is anonymized
- No personally identifiable information (PII) included
- Collected with informed consent
- For research and educational purposes

## Citation

If you use this data, please cite:

```
SSVEP-based BCI Dataset
Collected using OpenBCI Cyton Board
Available at: https://github.com/bw493/ssvep-bci-openbci
```

## Questions?

For questions about the data collection protocol or data quality:
- Open an issue on GitHub
- Check the main README.md for system documentation
