#!/usr/bin/env python3
"""
Convert OpenBCI raw data files to MNE-compatible FIF format

Supports:
- OpenBCI-RAW TXT files (from OpenBCI GUI)
- BrainFlow CSV files
"""

import numpy as np
import pandas as pd
import mne
import os
import sys
import argparse
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import CHANNELS, SAMPLING_RATE


def load_openbci_txt(filepath: str) -> tuple:
    """
    Load OpenBCI TXT format data
    
    Parameters:
    -----------
    filepath : str
        Path to OpenBCI-RAW .txt file
        
    Returns:
    --------
    data : ndarray
        EEG data (channels x samples)
    sfreq : float
        Sampling frequency
    ch_names : list
        Channel names
    """
    print(f"Loading OpenBCI TXT file: {filepath}")
    
    # Read the file, skipping header lines
    df = pd.read_csv(filepath, skiprows=5)
    
    # Extract EEG channels (columns 1-8 for 8-channel Cyton)
    eeg_columns = [f'EXG Channel {i}' for i in range(8)]
    
    # Check which columns exist
    available_channels = [col for col in eeg_columns if col in df.columns]
    
    if not available_channels:
        # Try alternate column format (without spaces)
        eeg_columns = [f'EXGChannel{i}' for i in range(8)]
        available_channels = [col for col in eeg_columns if col in df.columns]
    
    print(f"Found {len(available_channels)} EEG channels")
    
    # Extract data
    data = df[available_channels].values.T  # Transpose to (channels x samples)
    
    # Get sampling rate from header or use default
    sfreq = SAMPLING_RATE
    
    # Get channel names from config
    ch_names = CHANNELS[:len(available_channels)]
    
    print(f"Data shape: {data.shape}")
    print(f"Sampling rate: {sfreq} Hz")
    print(f"Duration: {data.shape[1] / sfreq:.2f} seconds")
    
    return data, sfreq, ch_names


def load_brainflow_csv(filepath: str) -> tuple:
    """
    Load BrainFlow CSV format data
    
    Parameters:
    -----------
    filepath : str
        Path to BrainFlow CSV file
        
    Returns:
    --------
    data : ndarray
        EEG data (channels x samples)
    sfreq : float
        Sampling frequency
    ch_names : list
        Channel names
    """
    print(f"Loading BrainFlow CSV file: {filepath}")
    
    # Read CSV (tab-separated)
    df = pd.read_csv(filepath, sep='\t', header=None)
    
    # BrainFlow format: columns 1-8 are EEG channels
    # Column 0 is sample index
    eeg_data = df.iloc[:, 1:9].values.T  # Transpose to (channels x samples)
    
    print(f"Found {eeg_data.shape[0]} EEG channels")
    
    # Get sampling rate
    sfreq = SAMPLING_RATE
    
    # Get timestamps if available (column 22)
    if df.shape[1] > 22:
        timestamps = df.iloc[:, 22].values
        # Calculate actual sampling rate from timestamps
        if len(timestamps) > 1:
            time_diffs = np.diff(timestamps)
            avg_diff = np.mean(time_diffs[time_diffs > 0])
            calculated_sfreq = 1.0 / avg_diff
            print(f"Calculated sampling rate from timestamps: {calculated_sfreq:.2f} Hz")
            # Use calculated rate if reasonable
            if 200 < calculated_sfreq < 300:
                sfreq = calculated_sfreq
    
    ch_names = CHANNELS[:eeg_data.shape[0]]
    
    print(f"Data shape: {eeg_data.shape}")
    print(f"Sampling rate: {sfreq} Hz")
    print(f"Duration: {eeg_data.shape[1] / sfreq:.2f} seconds")
    
    return eeg_data, sfreq, ch_names


def convert_to_fif(input_file: str, output_file: str = None) -> str:
    """
    Convert OpenBCI data to MNE FIF format
    
    Parameters:
    -----------
    input_file : str
        Path to input file (.txt or .csv)
    output_file : str, optional
        Path to output .fif file. If None, uses input filename with .fif extension
        
    Returns:
    --------
    output_path : str
        Path to created FIF file
    """
    print("\n" + "="*60)
    print("OpenBCI to FIF Converter")
    print("="*60 + "\n")
    
    # Determine file type and load data
    if input_file.endswith('.txt'):
        data, sfreq, ch_names = load_openbci_txt(input_file)
    elif input_file.endswith('.csv'):
        data, sfreq, ch_names = load_brainflow_csv(input_file)
    else:
        raise ValueError(f"Unsupported file format: {input_file}")
    
    # Convert from microvolts to volts (MNE standard)
    # OpenBCI data is typically in microvolts
    data = data * 1e-6
    
    # Create MNE info structure
    info = mne.create_info(
        ch_names=ch_names,
        sfreq=sfreq,
        ch_types='eeg'
    )
    
    # Create Raw object
    raw = mne.io.RawArray(data, info)
    
    # Set montage for standard 10-20 positions
    try:
        montage = mne.channels.make_standard_montage('standard_1020')
        raw.set_montage(montage, on_missing='warn')
        print("\n✓ Applied standard 10-20 montage")
    except Exception as e:
        print(f"\n⚠ Warning: Could not set montage: {e}")
    
    # Determine output filename
    if output_file is None:
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        output_file = f"{base_name}.fif"
    
    # Save to FIF format
    raw.save(output_file, overwrite=True, verbose='WARNING')
    
    print(f"\n✓ Saved to: {output_file}")
    print("="*60 + "\n")
    
    return output_file


def convert_directory(input_dir: str, output_dir: str = None):
    """
    Convert all OpenBCI files in a directory
    
    Parameters:
    -----------
    input_dir : str
        Directory containing OpenBCI data files
    output_dir : str, optional
        Directory for output FIF files
    """
    if output_dir is None:
        output_dir = input_dir
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all data files
    data_files = []
    for ext in ['*.txt', '*.csv']:
        data_files.extend(Path(input_dir).glob(ext))
    
    # Filter out non-data files
    data_files = [f for f in data_files if 'OpenBCI-RAW' in f.name or 'BrainFlow' in f.name]
    
    print(f"\nFound {len(data_files)} data file(s) to convert\n")
    
    converted = []
    for i, filepath in enumerate(data_files, 1):
        print(f"\n[{i}/{len(data_files)}] Processing: {filepath.name}")
        try:
            output_file = os.path.join(output_dir, filepath.stem + '.fif')
            convert_to_fif(str(filepath), output_file)
            converted.append(output_file)
        except Exception as e:
            print(f"✗ Error converting {filepath.name}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print(f"Conversion complete: {len(converted)}/{len(data_files)} successful")
    print("="*60 + "\n")
    
    return converted


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Convert OpenBCI data to MNE FIF format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert single file
  python convert_openbci_data.py --input data.txt --output data.fif
  
  # Convert all files in directory
  python convert_openbci_data.py --input-dir raw_data/ --output-dir processed/
  
  # Convert files in current directory
  python convert_openbci_data.py --input-dir .
        """
    )
    
    parser.add_argument('--input', type=str,
                       help='Input file (.txt or .csv)')
    parser.add_argument('--output', type=str,
                       help='Output FIF file')
    parser.add_argument('--input-dir', type=str,
                       help='Directory containing data files to convert')
    parser.add_argument('--output-dir', type=str,
                       help='Directory for output FIF files')
    
    args = parser.parse_args()
    
    if args.input:
        # Convert single file
        if not os.path.exists(args.input):
            print(f"Error: Input file not found: {args.input}")
            sys.exit(1)
        
        convert_to_fif(args.input, args.output)
        
    elif args.input_dir:
        # Convert directory
        if not os.path.exists(args.input_dir):
            print(f"Error: Input directory not found: {args.input_dir}")
            sys.exit(1)
        
        convert_directory(args.input_dir, args.output_dir)
        
    else:
        parser.print_help()
        print("\nError: Must specify either --input or --input-dir")
        sys.exit(1)
