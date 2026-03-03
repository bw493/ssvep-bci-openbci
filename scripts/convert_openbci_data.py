#!/usr/bin/env python3
"""
Fixed OpenBCI to FIF Converter
Handles both TXT files with % headers and BrainFlow CSV files
"""

import argparse
import numpy as np
import pandas as pd
import mne
from pathlib import Path
from typing import Tuple, Optional


def parse_openbci_txt(filepath: str) -> Tuple[np.ndarray, float, list]:
    """
    Parse OpenBCI GUI TXT format with % comment headers.
    
    Returns:
        data: (n_channels, n_samples) array
        sfreq: sampling frequency in Hz
        ch_names: list of channel names
    """
    print(f"\nLoading OpenBCI TXT file: {filepath}")
    
    # Read metadata from header
    sfreq = 250.0  # default
    n_channels = None
    
    with open(filepath, 'r') as f:
        for line in f:
            if line.startswith('%Sample Rate'):
                # Extract sample rate: "%Sample Rate = 250 Hz"
                parts = line.split('=')
                if len(parts) == 2:
                    sfreq = float(parts[1].strip().split()[0])
            elif line.startswith('%Number of channels'):
                # Extract channel count: "%Number of channels = 8"
                parts = line.split('=')
                if len(parts) == 2:
                    n_channels = int(parts[1].strip())
            elif not line.startswith('%'):
                # Reached data section
                break
    
    # Read CSV data, skipping % comment lines
    df = pd.read_csv(filepath, comment='%')
    
    # Find EXG channels (the actual EEG data)
    exg_cols = [col for col in df.columns if 'EXG Channel' in col]
    
    if len(exg_cols) == 0:
        raise ValueError("No EXG channels found in data")
    
    print(f"Found {len(exg_cols)} EEG channels")
    
    # Extract EEG data and transpose to (channels, samples)
    data = df[exg_cols].values.T
    
    # Create channel names
    ch_names = [f'EEG{i+1}' for i in range(len(exg_cols))]
    
    print(f"Data shape: {data.shape}")
    print(f"Sampling rate: {sfreq} Hz")
    print(f"Duration: {data.shape[1] / sfreq:.2f} seconds")
    
    return data, sfreq, ch_names


def parse_brainflow_csv(filepath: str) -> Tuple[np.ndarray, float, list]:
    """
    Parse BrainFlow CSV format.
    
    Returns:
        data: (n_channels, n_samples) array
        sfreq: sampling frequency in Hz
        ch_names: list of channel names
    """
    print(f"\nLoading BrainFlow CSV file: {filepath}")
    
    df = pd.read_csv(filepath)
    
    # Find EEG channels (columns 1-8 for Cyton board)
    # BrainFlow format typically has EEG in first columns
    eeg_cols = [col for col in df.columns if col.isdigit() and int(col) <= 8]
    
    if len(eeg_cols) == 0:
        # Try alternative naming
        eeg_cols = [col for col in df.columns if 'EXG' in str(col) or 'EEG' in str(col)]
    
    if len(eeg_cols) == 0:
        # Assume first 8 numeric columns are EEG
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        eeg_cols = numeric_cols[:8]
    
    print(f"Found {len(eeg_cols)} EEG channels")
    
    # Extract data
    data = df[eeg_cols].values.T
    
    # Calculate sampling rate from timestamps if available
    if 'timestamp' in df.columns:
        timestamps = df['timestamp'].values
        time_diff = np.diff(timestamps)
        sfreq = 1.0 / np.median(time_diff)
        print(f"Calculated sampling rate from timestamps: {sfreq:.2f} Hz")
    else:
        sfreq = 250.0  # default for OpenBCI
        print(f"Using default sampling rate: {sfreq} Hz")
    
    # Create channel names
    ch_names = [f'EEG{i+1}' for i in range(len(eeg_cols))]
    
    print(f"Data shape: {data.shape}")
    print(f"Sampling rate: {sfreq} Hz")
    print(f"Duration: {data.shape[1] / sfreq:.2f} seconds")
    
    return data, sfreq, ch_names


def convert_to_fif(input_file: str, output_file: str):
    """
    Convert OpenBCI data file to MNE FIF format.
    """
    print("\n" + "="*60)
    print("OpenBCI to FIF Converter")
    print("="*60)
    
    # Detect file format and parse
    if input_file.endswith('.txt'):
        data, sfreq, ch_names = parse_openbci_txt(input_file)
    elif input_file.endswith('.csv'):
        data, sfreq, ch_names = parse_brainflow_csv(input_file)
    else:
        raise ValueError(f"Unsupported file format: {input_file}")
    
    # Validate data
    if data.shape[0] == 0:
        raise ValueError("No channels found in data")
    if data.shape[1] == 0:
        raise ValueError("No samples found in data")
    
    # Create MNE info structure
    info = mne.create_info(
        ch_names=ch_names,
        sfreq=sfreq,
        ch_types=['eeg'] * len(ch_names)
    )
    
    # Create RawArray
    raw = mne.io.RawArray(data, info, verbose='WARNING')
    
    # Set standard 10-20 montage for Cyton board
    # Map our channels to actual electrode positions from your setup
    if len(ch_names) == 8:
        montage_mapping = {
            'EEG1': 'Fp1',  # Frontal pole left
            'EEG2': 'Fz',   # Frontal midline
            'EEG3': 'F3',   # Frontal left
            'EEG4': 'F4',   # Frontal right
            'EEG5': 'F7',   # Frontal temporal left
            'EEG6': 'F8',   # Frontal temporal right
            'EEG7': 'O1',   # Occipital left
            'EEG8': 'O2'    # Occipital right
        }
        raw.rename_channels(montage_mapping)
        montage = mne.channels.make_standard_montage('standard_1020')
        raw.set_montage(montage, on_missing='warn')
        print("✓ Applied standard 10-20 montage with actual electrode positions")
    
    # Save to FIF format
    raw.save(output_file, overwrite=True, verbose='WARNING')
    
    print(f"\n✓ Saved to: {output_file}")
    print("="*60 + "\n")


def convert_directory(input_dir: str, output_dir: str):
    """
    Convert all OpenBCI files in a directory.
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find all data files
    data_files = list(input_path.glob('*.txt')) + list(input_path.glob('*.csv'))
    
    if not data_files:
        print(f"No data files found in {input_dir}")
        return
    
    print(f"\nFound {len(data_files)} data file(s) to convert\n")
    
    success_count = 0
    for i, filepath in enumerate(data_files, 1):
        print(f"\n[{i}/{len(data_files)}] Processing: {filepath.name}")
        
        # Generate output filename (use _raw.fif convention)
        output_file = output_path / f"{filepath.stem}_raw.fif"
        
        try:
            convert_to_fif(str(filepath), str(output_file))
            success_count += 1
        except Exception as e:
            print(f"✗ Error converting {filepath.name}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print(f"Conversion complete: {success_count}/{len(data_files)} successful")
    print("="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Convert OpenBCI data files to MNE FIF format'
    )
    parser.add_argument(
        '--input-file',
        type=str,
        help='Input data file (.txt or .csv)'
    )
    parser.add_argument(
        '--output-file',
        type=str,
        help='Output FIF file'
    )
    parser.add_argument(
        '--input-dir',
        type=str,
        help='Directory containing input files'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        help='Directory for output files'
    )
    
    args = parser.parse_args()
    
    if args.input_file and args.output_file:
        # Single file conversion
        convert_to_fif(args.input_file, args.output_file)
    elif args.input_dir and args.output_dir:
        # Directory conversion
        convert_directory(args.input_dir, args.output_dir)
    else:
        parser.print_help()
        print("\nError: Provide either --input-file/--output-file or --input-dir/--output-dir")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
