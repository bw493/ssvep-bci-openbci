# Quick Start Guide - Using Your Collected Data

This guide shows how to process and analyze the SSVEP data you collected.

## Step 1: Convert Your Data

Your team collected 4 data files. Convert them to FIF format:

```bash
# Convert all at once
python scripts/convert_openbci_data.py --input-dir data/raw --output-dir data/processed
```

This will create:
- `data/processed/OpenBCI-RAW-2026-02-23_19-06-24.fif`
- `data/processed/OpenBCI-RAW-2026-02-26_19-22-57.fif`
- `data/processed/OpenBCI-RAW-2026-02-26_19-35-13.fif`
- `data/processed/BrainFlow-RAW_2026-02-23_19-05-38_0.fif`

## Step 2: Run the Pipeline on Session 1

```bash
python scripts/run_pipeline.py --data data/processed/OpenBCI-RAW-2026-02-23_19-06-24.fif
```

This will:
1. Load the data
2. Apply filters (notch + bandpass)
3. Re-reference to CAR
4. Run ICA for artifacts
5. Extract CSP features
6. Train LDA classifier
7. Send simulated Arduino commands

## Step 3: Analyze All Sessions

Process each session to compare results:

```bash
# Session 1 (Feb 23)
python scripts/run_pipeline.py --data data/processed/OpenBCI-RAW-2026-02-23_19-06-24.fif

# Session 2 (Feb 26 - morning)
python scripts/run_pipeline.py --data data/processed/OpenBCI-RAW-2026-02-26_19-22-57.fif

# Session 3 (Feb 26 - afternoon)
python scripts/run_pipeline.py --data data/processed/OpenBCI-RAW-2026-02-26_19-35-13.fif
```

## Step 4: Try Different Configurations

### Use PSD features instead of CSP:
```bash
python scripts/run_pipeline.py --data data/processed/OpenBCI-RAW-2026-02-23_19-06-24.fif --no-csp
```

### Use SVM instead of LDA:
Edit `config/config.py`:
```python
CLASSIFIER_TYPE = 'svm'  # Change from 'lda'
```

Then run again.

## Expected Results

For good SSVEP data, you should see:
- **Preprocessing**: Removal of power line noise and artifacts
- **Feature Extraction**: Clear power peaks at SSVEP frequencies (7 Hz and 9 Hz)
- **Classification**: Accuracy > 70% (good), > 85% (excellent)
- **Arduino Control**: Correct commands sent based on predictions

## Troubleshooting

### "No events found in data"
The pipeline will create synthetic events for testing. This is normal for continuous recordings without event markers.

### Low Classification Accuracy (<60%)
Possible causes:
- Weak SSVEP response (check data quality)
- Too many artifacts (check ICA removed them)
- Need more training data (collect more trials)

Try:
```bash
# Use more CSP components
# Edit config/config.py:
N_CSP_COMPONENTS = 6  # Instead of 4
```

### "Channel not found" Error
Your data might be using different channel names. Check:
```python
# In convert_openbci_data.py, around line 35
# Update channel mapping if needed
```

## Next Steps

### 1. Combine Sessions for Better Training
Merge data from multiple sessions:
```python
# Custom script to combine sessions
import mne

raw1 = mne.io.read_raw_fif('data/processed/session1.fif')
raw2 = mne.io.read_raw_fif('data/processed/session2.fif')
raw_combined = mne.concatenate_raws([raw1, raw2])
raw_combined.save('data/processed/combined.fif')
```

### 2. Visualize Your Data
```python
import mne

raw = mne.io.read_raw_fif('data/processed/OpenBCI-RAW-2026-02-23_19-06-24.fif')

# Plot raw data
raw.plot(duration=10, n_channels=8)

# Plot power spectrum
raw.plot_psd(fmax=50)
```

### 3. Real-Time Processing
For live BCI control:
1. Stream from OpenBCI using LSL
2. Process in real-time chunks
3. Send immediate commands to Arduino

See documentation for real-time implementation.

## Files Generated

After running the pipeline, you'll have:
```
data/
├── raw/                    # Your original data (unchanged)
├── processed/              # Converted FIF files
└── results/               # Analysis outputs (optional)
    ├── classification_results.txt
    ├── feature_plots/
    └── ica_components/
```

## Getting Help

- Check main README.md for detailed documentation
- See GITHUB_SETUP.md for pushing to repository
- Open an issue on GitHub for bugs or questions

## Performance Tips

**For faster processing:**
1. Use LDA instead of SVM (already default)
2. Reduce ICA components: `ICA_N_COMPONENTS = 0.95` (instead of 0.99)
3. Use shorter epochs if real-time is needed

**For better accuracy:**
1. Collect more trials (>32)
2. Use both CSP and PSD features combined
3. Ensemble multiple classifiers
