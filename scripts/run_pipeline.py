#!/usr/bin/env python3
"""
Main pipeline script for SSVEP-based BCI system
Runs the complete end-to-end pipeline from data loading to device control
"""

import numpy as np
import mne
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import *
from preprocessing import (
    load_raw_data, select_channels, get_data_info,
    apply_filtering_pipeline, apply_common_average_reference,
    run_ica_pipeline
)
from features import create_psd_features, apply_csp
from classification import train_classifier, evaluate_classifier, predict_command
from control import ArduinoController


def create_epochs(raw: mne.io.Raw,
                 event_id: dict,
                 tmin: float = 0.0,
                 tmax: float = 12.0) -> mne.Epochs:
    """
    Create epochs from continuous data
    
    Parameters:
    -----------
    raw : mne.io.Raw
        Continuous EEG data
    event_id : dict
        Mapping of event names to event codes
    tmin : float
        Start time before event (seconds)
    tmax : float
        End time after event (seconds)
        
    Returns:
    --------
    epochs : mne.Epochs
        Epoched data
    """
    print("\n=== Creating Epochs ===")
    
    # Find events in the data
    # In real data, events would be marked during recording
    # For simulation, we create synthetic events
    events = mne.find_events(raw, stim_channel='STI 014', verbose='WARNING')
    
    if len(events) == 0:
        print("No events found in data. Creating synthetic events for demonstration...")
        # Create synthetic events
        n_events = N_TRIALS
        sfreq = raw.info['sfreq']
        event_spacing = int(sfreq * (tmax - tmin + 2))  # 2 seconds between trials
        
        events = np.zeros((n_events, 3), dtype=int)
        events[:, 0] = np.arange(n_events) * event_spacing + int(sfreq)
        events[:, 2] = np.random.choice(list(event_id.values()), n_events)
    
    print(f"Found {len(events)} events")
    
    # Create epochs
    epochs = mne.Epochs(
        raw, events, event_id,
        tmin=tmin, tmax=tmax,
        baseline=None,
        preload=True,
        verbose='WARNING'
    )
    
    print(f"Created {len(epochs)} epochs")
    print(f"Epoch duration: {tmax - tmin} seconds")
    
    return epochs


def run_pipeline(data_file: str,
                simulation_mode: bool = True,
                use_csp: bool = USE_CSP):
    """
    Run the complete SSVEP BCI pipeline
    
    Parameters:
    -----------
    data_file : str
        Path to EEG data file (.fif format)
    simulation_mode : bool
        If True, simulate Arduino commands without hardware
    use_csp : bool
        Whether to use CSP features
    """
    print("\n" + "="*60)
    print("SSVEP-BASED BCI PIPELINE")
    print("="*60 + "\n")
    
    # ========== STEP 1: Load Data ==========
    print("\n### STEP 1: DATA LOADING ###")
    raw = load_raw_data(data_file)
    raw = select_channels(raw)
    info = get_data_info(raw)
    
    # ========== STEP 2: Preprocessing ==========
    print("\n### STEP 2: PREPROCESSING ###")
    
    # Filtering
    raw = apply_filtering_pipeline(raw, notch=True, bandpass=True)
    
    # Re-referencing
    raw = apply_common_average_reference(raw)
    
    # ICA for artifact removal
    raw_clean, ica = run_ica_pipeline(raw, auto_detect=True)
    
    # ========== STEP 3: Epoching ==========
    print("\n### STEP 3: EPOCHING ###")
    event_id = {'OPEN': 1, 'CLOSE': 2}
    epochs = create_epochs(raw_clean, event_id, tmin=0.0, tmax=TRIAL_DURATION)
    
    # ========== STEP 4: Feature Extraction ==========
    print("\n### STEP 4: FEATURE EXTRACTION ###")
    
    # Get labels
    labels = epochs.events[:, -1]
    labels = np.where(labels == 1, 0, 1)  # Convert to 0/1
    
    if use_csp:
        # Split data for training
        n_train = int(0.8 * len(epochs))
        
        # Get data in format for CSP (trials x channels x samples)
        data = epochs.get_data()
        X_train = data[:n_train]
        X_test = data[n_train:]
        y_train = labels[:n_train]
        y_test = labels[n_train:]
        
        # Apply CSP
        features_train, features_test, csp = apply_csp(
            X_train, y_train, X_test, N_CSP_COMPONENTS
        )
    else:
        # Use PSD features
        features = create_psd_features(epochs, use_snr=False)
        
        # Split data
        n_train = int(0.8 * len(features))
        features_train = features[:n_train]
        features_test = features[n_train:]
        y_train = labels[:n_train]
        y_test = labels[n_train:]
    
    # ========== STEP 5: Classification ==========
    print("\n### STEP 5: CLASSIFICATION ###")
    
    # Train classifier
    classifier = train_classifier(
        features_train, y_train,
        classifier_type=CLASSIFIER_TYPE
    )
    
    # Evaluate
    results = evaluate_classifier(
        classifier, features_test, y_test,
        class_names=['OPEN', 'CLOSE']
    )
    
    # ========== STEP 6: Device Control ==========
    print("\n### STEP 6: DEVICE CONTROL ###")
    
    # Create command map
    command_map = {0: 'OPEN', 1: 'CLOSE'}
    
    # Initialize Arduino controller
    with ArduinoController(simulation_mode=simulation_mode) as arduino:
        print("\nSending test commands...")
        
        # Test with a few predictions
        for i in range(min(5, len(features_test))):
            # Predict command
            prediction = classifier.predict(features_test[i:i+1])[0]
            command = command_map[prediction]
            true_label = command_map[y_test[i]]
            
            print(f"\nTrial {i+1}:")
            print(f"  True class: {true_label}")
            print(f"  Predicted: {command}")
            print(f"  Match: {'✓' if prediction == y_test[i] else '✗'}")
            
            # Send command to Arduino
            arduino.send_command(command)
            
            import time
            time.sleep(0.5)
    
    # ========== Pipeline Complete ==========
    print("\n" + "="*60)
    print("PIPELINE COMPLETE")
    print("="*60)
    print(f"\nFinal Test Accuracy: {results['accuracy']:.2%}")
    print(f"Total trials processed: {len(epochs)}")
    print(f"Training samples: {len(features_train)}")
    print(f"Test samples: {len(features_test)}")
    
    return {
        'classifier': classifier,
        'results': results,
        'raw_clean': raw_clean,
        'epochs': epochs,
        'features_train': features_train,
        'features_test': features_test
    }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Run SSVEP BCI Pipeline')
    parser.add_argument('--data', type=str, default='../data/ssvep_data_raw.fif',
                       help='Path to EEG data file')
    parser.add_argument('--no-simulation', action='store_true',
                       help='Use real Arduino (default: simulation mode)')
    parser.add_argument('--no-csp', action='store_true',
                       help='Disable CSP features (use PSD only)')
    
    args = parser.parse_args()
    
    # Check if data file exists
    if not os.path.exists(args.data):
        print(f"Error: Data file not found: {args.data}")
        print("\nThis script expects EEG data in FIF format.")
        print("To run with your own data:")
        print(f"  1. Place your .fif file in the data/ directory")
        print(f"  2. Run: python run_pipeline.py --data path/to/your/data.fif")
        print("\nFor testing without data, create a synthetic data file first.")
        sys.exit(1)
    
    # Run pipeline
    try:
        output = run_pipeline(
            args.data,
            simulation_mode=not args.no_simulation,
            use_csp=not args.no_csp
        )
        print("\n✓ Pipeline executed successfully!")
        
    except Exception as e:
        print(f"\n✗ Pipeline failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
