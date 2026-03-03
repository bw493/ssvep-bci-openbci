"""
Configuration file for SSVEP BCI system
Contains all experimental parameters and settings
"""

# EEG Acquisition Settings
CHANNELS = ['Cz', 'C3', 'C4', 'CPz', 'F3', 'F4', 'P3', 'P4']
SAMPLING_RATE = 250  # Hz (typical for OpenBCI Cyton)

# Experiment Protocol
N_TRIALS = 32
N_RUNS = 8
TRIALS_PER_RUN = 4
TRIAL_DURATION = 12  # seconds

# Pre-processing Parameters
NOTCH_FREQ = 50  # Hz (power line noise)
BANDPASS_LOW = 6  # Hz
BANDPASS_HIGH = 40  # Hz

# ICA Parameters
ICA_N_COMPONENTS = 0.99  # Explained variance threshold
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
N_CSP_COMPONENTS = 4

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
