# SSVEP-Based Brain-Computer Interface (BCI) System

A complete Python implementation of an SSVEP-based Brain-Computer Interface for controlling a bionic hand using OpenBCI and Arduino.

## Overview

This system implements a closed-loop BCI pipeline that:
1. Acquires EEG signals using OpenBCI hardware
2. Processes signals through filtering, ICA, and re-referencing
3. Extracts SSVEP features using CSP and PSD methods
4. Classifies user intent (OPEN/CLOSE commands) using LDA or SVM
5. Controls a bionic hand via Arduino serial communication

## System Architecture

```
EEG Acquisition (OpenBCI) → Pre-processing (MNE) → Feature Extraction (CSP/PSD) 
→ Classification (LDA/SVM) → Device Control (Arduino) → Bionic Hand
```

## Requirements

- Python 3.8+
- OpenBCI Cyton Board (for real data acquisition)
- Arduino UNO (for bionic hand control)
- PsychoPy (for stimulus presentation)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/bw493/ssvep-bci-openbci.git
cd ssvep-bci-openbci
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Configure settings in `config/config.py`:
   - Update `ARDUINO_PORT` to match your system
   - Adjust SSVEP frequencies if needed
   - Set classifier parameters

## Project Structure

```
ssvep_bci/
├── config/
│   └── config.py              # System configuration
├── preprocessing/
│   ├── load_data.py           # Data loading utilities
│   ├── filters.py             # Notch and bandpass filters
│   ├── rereference.py         # Common Average Reference
│   └── ica.py                 # ICA artifact removal
├── features/
│   ├── psd_features.py        # Power Spectral Density features
│   ├── csp.py                 # Common Spatial Pattern
│   └── laplacian.py           # Surface Laplacian filtering
├── classification/
│   └── classifier.py          # LDA and SVM classifiers
├── control/
│   └── arduino_control.py     # Arduino serial communication
├── scripts/
│   ├── run_pipeline.py        # Main pipeline execution
│   ├── generate_test_data.py  # Generate synthetic test data
│   └── convert_openbci_data.py # Convert OpenBCI files to FIF
├── data/
│   ├── raw/                   # Collected OpenBCI data (4 sessions)
│   └── processed/             # Converted FIF files
├── QUICKSTART.md              # Quick start with collected data
├── GITHUB_SETUP.md            # GitHub repository setup guide
└── README.md                  # This file
```

## Quick Start

### Option 1: Use Collected Data (Recommended)

The repository includes real EEG data collected with OpenBCI:

```bash
# 1. Convert your collected data to FIF format
python scripts/convert_openbci_data.py --input-dir data/raw --output-dir data/processed

# 2. Run pipeline on Session 1
python scripts/run_pipeline.py --data data/processed/OpenBCI-RAW-2026-02-23_19-06-24.fif
```

See **QUICKSTART.md** for detailed instructions on using your collected data.

### Option 2: Generate Synthetic Test Data

For testing without real EEG hardware:

```bash
python scripts/generate_test_data.py
```

This creates `data/ssvep_data_raw.fif` with synthetic SSVEP responses.

### 2. Run the Pipeline

**Simulation Mode (no Arduino required):**
```bash
python scripts/run_pipeline.py --data data/ssvep_data_raw.fif
```

**With Real Arduino:**
```bash
python scripts/run_pipeline.py --data data/ssvep_data_raw.fif --no-simulation
```

**Using PSD features instead of CSP:**
```bash
python scripts/run_pipeline.py --data data/ssvep_data_raw.fif --no-csp
```

## Experimental Protocol

- **Electrodes:** Cz, C3, C4, CPz, F3, F4, P3, P4
- **Sampling Rate:** 250 Hz (OpenBCI Cyton default)
- **Trials:** 32 total (8 runs × 4 trials per run)
- **Trial Duration:** 12 seconds
- **SSVEP Frequencies:**
  - OPEN: 7.0 Hz
  - CLOSE: 9.0 Hz

## Pre-processing Pipeline

1. **Filtering:**
   - Notch filter at 50 Hz (power line noise)
   - Bandpass filter: 6-40 Hz

2. **Re-referencing:**
   - Common Average Reference (CAR)

3. **Artifact Removal:**
   - Independent Component Analysis (ICA)
   - Automatic artifact detection

## Feature Extraction

### Common Spatial Pattern (CSP)
- Maximizes variance between classes
- Default: 4 components (2 from each end)

### Power Spectral Density (PSD)
- Welch's method for spectral estimation
- Extracts power at SSVEP frequencies
- Optional SNR computation

### Surface Laplacian
- Spatial sharpening for enhanced features
- Local average reference

## Classification

**Linear Discriminant Analysis (LDA)** (default)
- Fast, efficient for binary classification
- Good for real-time BCI

**Support Vector Machine (SVM)**
- Linear kernel by default
- Configurable C parameter

## Arduino Control

### Hardware Setup

1. **Connect Arduino UNO** to your computer
2. **Update port** in `config/config.py`:
   - Windows: `COM3`, `COM4`, etc.
   - Linux: `/dev/ttyUSB0`, `/dev/ttyACM0`
   - Mac: `/dev/cu.usbmodem*`

### Arduino Sketch

Upload this sketch to your Arduino:

```cpp
// SSVEP BCI - Bionic Hand Control
const int THUMB_PIN = 9;
const int FINGER_PIN = 10;

void setup() {
  Serial.begin(9600);
  pinMode(THUMB_PIN, OUTPUT);
  pinMode(FINGER_PIN, OUTPUT);
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read();
    
    if (command == 'O') {
      // OPEN command
      digitalWrite(THUMB_PIN, HIGH);
      digitalWrite(FINGER_PIN, HIGH);
      Serial.println("Hand OPEN");
    }
    else if (command == 'C') {
      // CLOSE command
      digitalWrite(THUMB_PIN, LOW);
      digitalWrite(FINGER_PIN, LOW);
      Serial.println("Hand CLOSE");
    }
  }
}
```

## Using with Real EEG Data

### Data Acquisition

1. **OpenBCI Setup:**
   - Mount EEG cap with electrodes at specified locations
   - Connect to Cyton Board
   - Use OpenBCI GUI with LSL plugin

2. **Streaming to Python:**
   ```bash
   python openbci_lsl.py
   ```

3. **Recording:**
   - Record in FIF format using MNE
   - Include event markers for trial timing

### PsychoPy Stimulus

Create an SSVEP stimulus interface:
- Flicker targets at 7.0 Hz (OPEN) and 9.0 Hz (CLOSE)
- Trial duration: 12 seconds
- Send event markers via LSL

## Configuration

Edit `config/config.py` to customize:

```python
# EEG channels
CHANNELS = ['Cz', 'C3', 'C4', 'CPz', 'F3', 'F4', 'P3', 'P4']

# SSVEP frequencies
SSVEP_FREQS = {
    'OPEN': 7.0,
    'CLOSE': 9.0
}

# Classifier
CLASSIFIER_TYPE = 'lda'  # or 'svm'

# Arduino
ARDUINO_PORT = 'COM3'  # Update for your system
```

## Troubleshooting

### Arduino Connection Issues

**Error:** "Failed to connect to Arduino"
- Check cable connection
- Verify correct port in `config/config.py`
- Ensure Arduino IDE is closed (releases serial port)
- Check Arduino is not in use by another program

### Data Loading Issues

**Error:** "Data file not found"
- Generate test data: `python scripts/generate_test_data.py`
- Check file path is correct
- Ensure data directory exists

### Import Errors

**Error:** "No module named 'mne'"
- Install dependencies: `pip install -r requirements.txt`
- Use virtual environment if needed

## Performance Optimization

For real-time BCI applications:

1. **Use LDA** instead of SVM (faster)
2. **Reduce ICA components** (faster fitting)
3. **Use CSP features** (fewer features than PSD)
4. **Optimize epoch length** (shorter = faster, but less accurate)

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## References

- OpenBCI Documentation: https://docs.openbci.com/
- MNE-Python: https://mne.tools/
- CSP for BCI: Blankertz et al. (2008)
- SSVEP-based BCI: Vialatte et al. (2010)

## License

This project is licensed under the MIT License.

## Authors

- bw493 (GitHub)

## Acknowledgments

- OpenBCI community
- MNE-Python developers
- Brain-Computer Interface research community
