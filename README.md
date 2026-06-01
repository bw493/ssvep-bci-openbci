# neuroflow-eeg-analytics

A browser-based EEG analytics platform for uploading, processing, and visualizing electroencephalography data from CSV files. The application runs on a local development server and requires no external hardware or cloud services.

## Overview

neuroflow-eeg-analytics provides an interactive web interface for EEG data analysis. Users upload CSV files exported from recording software, and the application processes and renders the data directly in the browser. All computation occurs locally on the network.

## Requirements

- Node.js 18+
- npm 9+

## Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/bw493/neuroflow-eeg-analytics.git
cd neuroflow-eeg-analytics
npm install
```

## Running the Application

Start the local development server:

```bash
npm run dev
```

Vite will compile the project and print the local URL:

```
  VITE v5.x.x  ready

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

Open `http://localhost:5173` in your browser to access the application.

To expose the server to other devices on the same local network, run:

```bash
npm run dev -- --host
```

Vite will then display a network address such as `http://192.168.x.x:5173` that other devices on the same network can access.

## Usage

1. Launch the application at the local URL.
2. Upload an EEG data file in CSV format using the file input interface.
3. The application parses the CSV, reads channel and timing metadata, and renders the analysis pipeline results in the browser.
4. Adjust analysis parameters through the interface controls as needed.

## Data Format

The application expects CSV files structured with time-series EEG channel data. A `metadata.json` file can accompany the CSV to supply channel names, sampling rate, and session information. Refer to `eeg_trial_data.csv` in the repository root for a reference example.

## Project Structure

```
neuroflow-eeg-analytics/
├── src/                    # Application source code
├── index.html              # Entry point
├── vite.config.ts          # Vite configuration
├── tsconfig.json           # TypeScript configuration
├── package.json            # Dependencies and scripts
├── .env.example            # Environment variable template
├── eeg_trial_data.csv      # Reference EEG data file
├── metadata.json           # Channel and session metadata
└── README.md               # This file
```
