# EEG Acquisition Settings
CHANNELS = ['O1', 'O2']  # Occipital channels for SSVEP (visual cortex)
SAMPLING_RATE = 250  # Hz (typical for OpenBCI Cyton)

# Experiment Protocol
N_TRIALS = 32
N_RUNS = 8
TRIALS_PER_RUN = 4
TRIAL_DURATION = 12  # seconds

# Pre-processing Parameters
NOTCH_FREQ = 60  # Hz (power line noise - use 50 for Europe, 60 for US)
BANDPASS_LOW = 6  # Hz
BANDPASS_HIGH = 40  # Hz

# ICA Parameters
ICA_N_COMPONENTS = 2  # Must be <= number of channels (was 6, now 2 for O1/O2)
ICA_METHOD = 'fastica'
ICA_RANDOM_STATE = 42

# SSVEP Frequencies
SSVEP_FREQS = {
    'OPEN': 7.0,   # Hz
    'CLOSE': 9.0   # Hz
}

# Classification Parameters
CLASSIFIER_TYPE = 'lda'  # Options: 'lda', 'svm'
SVM_KERNEL = 'linear'
SVM_C = 1.0

# Feature Extraction
USE_CSP = True
USE_LAPLACIAN = True
N_CSP_COMPONENTS = 2  # Changed from 4 to 2 (must be <= number of channels)

# Arduino Control
ARDUINO_PORT = 'COM3'  # Update based on your system
ARDUINO_BAUDRATE = 9600
COMMANDS = {
    'OPEN': b'O',
    'CLOSE': b'C'
}

# File Paths
DATA_DIR = 'data/'
OUTPUT_DIR = 'output/'