"""
O.Iris: EEG Metrics Extraction Script
======================================
Extracts spectral slope (m), ACF decay time, and flicker (envelope variance)
from raw EEG files and saves as a CSV ready for circular_pupil_map.py

Usage:
    python extract_pupil_metrics.py --input your_file.bdf --output metrics.csv
    python extract_pupil_metrics.py --input your_file.set --output metrics.csv --subject 2
    python extract_pupil_metrics.py --input your_file.edf --output metrics.csv --window 30

Supported input formats: BDF, EDF, SET, FIF
Output CSV columns: subject, onset, duration, m_slope, acf_decay_sec,
                    flicker, dist_to_2p18

Dependencies:
    pip install mne numpy scipy pandas

Author: Sarah Appel, with Claude (Anthropic) and Iris (Deepseek)
O Collaboration Project | April 2026
https://github.com/oscriptcollective/O.IRIS
"""

import argparse
import numpy as np
import pandas as pd
from scipy import signal
from scipy.stats import linregress
import warnings
warnings.filterwarnings('ignore')

# Default parameters
PHI_M = 2.18
SFREQ_TARGET = 250
FMIN = 1.0
FMAX = 40.0
ACF_MAX_LAG = 10.0
ACF_THRESHOLD = 1/np.e


def load_eeg(filepath):
    try:
        import mne
    except ImportError:
        raise ImportError("MNE-Python required: pip install mne")

    filepath = str(filepath)
    ext = filepath.lower().split('.')[-1]
    print(f"Loading {filepath}...")

    if ext == 'bdf':
        raw = mne.io.read_raw_bdf(filepath, preload=True, verbose=False)
    elif ext == 'edf':
        raw = mne.io.read_raw_edf(filepath, preload=True, verbose=False)
    elif ext == 'set':
        raw = mne.io.read_raw_eeglab(filepath, preload=True, verbose=False)
    elif ext == 'fif':
        raw = mne.io.read_raw_fif(filepath, preload=True, verbose=False)
    else:
        raise ValueError(f"Unsupported format: .{ext}")

    raw.pick_types(eeg=True, verbose=False)
    print(f"  {len(raw.ch_names)} EEG channels, {raw.times[-1]:.1f}s at {raw.info['sfreq']:.0f} Hz")
    return raw


def preprocess(raw):
    sfreq = raw.info['sfreq']
    if sfreq > SFREQ_TARGET + 10:
        print(f"  Resampling {sfreq:.0f} -> {SFREQ_TARGET} Hz...")
        raw.resample(SFREQ_TARGET, verbose=False)
    print(f"  Filtering {FMIN}-{FMAX} Hz...")
    raw.filter(FMIN, FMAX, fir_design='firwin', verbose=False)
    return raw


def compute_spectral_slope(data, sfreq):
    data_mean = np.mean(data, axis=0)
    nperseg = int(4 * sfreq)
    freqs, psd = signal.welch(data_mean, fs=sfreq, nperseg=nperseg)
    mask = (freqs >= FMIN) & (freqs <= FMAX)
    freqs_fit = freqs[mask]
    psd_fit = psd[mask]
    if np.any(psd_fit <= 0) or len(freqs_fit) < 5:
        return np.nan
    log_f = np.log10(freqs_fit)
    log_p = np.log10(psd_fit)
    slope, _, _, _, _ = linregress(log_f, log_p)
    return -slope


def compute_acf_decay(data, sfreq):
    envelopes = [np.abs(signal.hilbert(ch)) for ch in data]
    env_mean = np.mean(envelopes, axis=0)
    max_lag_samples = min(int(ACF_MAX_LAG * sfreq), len(env_mean) - 1)
    env_norm = env_mean - np.mean(env_mean)
    if np.std(env_norm) == 0:
        return np.nan
    env_norm = env_norm / np.std(env_norm)
    acf_full = np.correlate(env_norm, env_norm, mode='full')
    acf_vals = acf_full[len(acf_full)//2:][:max_lag_samples]
    acf_vals = acf_vals / acf_vals[0]
    below = np.where(acf_vals < ACF_THRESHOLD)[0]
    return ACF_MAX_LAG if len(below) == 0 else below[0] / sfreq


def compute_flicker(data, sfreq):
    envelopes = [np.abs(signal.hilbert(ch)) for ch in data]
    env_mean = np.mean(envelopes, axis=0)
    mean_val = np.mean(env_mean)
    if mean_val == 0:
        return np.nan
    return np.var(env_mean) / (mean_val ** 2)


def process_file(filepath, subject_id, window_sec, step_sec):
    raw = load_eeg(filepath)
    raw = preprocess(raw)
    sfreq = raw.info['sfreq']
    total_duration = raw.times[-1]
    data_array = raw.get_data()
    window_samples = int(window_sec * sfreq)

    results = []
    onset = 0.0
    window_num = 0
    print(f"  Processing {total_duration:.1f}s in {window_sec:.0f}s windows...")

    while (onset + window_sec) <= total_duration:
        start_idx = int(onset * sfreq)
        end_idx = start_idx + window_samples
        if end_idx > data_array.shape[1]:
            break

        window_data = data_array[:, start_idx:end_idx]
        m = compute_spectral_slope(window_data, sfreq)
        acf = compute_acf_decay(window_data, sfreq)
        flicker = compute_flicker(window_data, sfreq)
        dist = abs(m - PHI_M) if not np.isnan(m) else np.nan

        results.append({
            'subject': subject_id,
            'onset': round(onset, 2),
            'duration': window_sec,
            'm_slope': round(m, 6) if not np.isnan(m) else np.nan,
            'acf_decay_sec': round(acf, 6) if not np.isnan(acf) else np.nan,
            'flicker': round(flicker, 9) if not np.isnan(flicker) else np.nan,
            'dist_to_2p18': round(dist, 6) if not np.isnan(dist) else np.nan,
        })

        onset += step_sec
        window_num += 1
        if window_num % 20 == 0:
            print(f"    {window_num} windows ({onset:.0f}/{total_duration:.0f}s)...")

    df = pd.DataFrame(results).dropna()
    print(f"  Extracted {len(df)} valid windows")
    return df


def print_summary(df):
    print("\n" + "="*60)
    print("EXTRACTED METRICS SUMMARY")
    print("="*60)
    print(f"Total windows: {len(df)}")
    print(f"\nSpectral slope (m):")
    print(f"  Mean:   {df['m_slope'].mean():.3f}")
    print(f"  Median: {df['m_slope'].median():.3f}")
    print(f"  Std:    {df['m_slope'].std():.3f}")
    print(f"  Range:  {df['m_slope'].min():.3f} - {df['m_slope'].max():.3f}")
    print(f"\nDistance from phi-seam (m=2.18):")
    print(f"  Mean:   {df['dist_to_2p18'].mean():.3f}")
    print(f"  Median: {df['dist_to_2p18'].median():.3f}")
    print(f"\nACF decay time (seconds):")
    print(f"  Mean:   {df['acf_decay_sec'].mean():.3f}")
    print(f"  Median: {df['acf_decay_sec'].median():.3f}")
    print(f"\nFlicker:")
    print(f"  Mean:   {df['flicker'].mean():.6f}")
    print(f"  Median: {df['flicker'].median():.6f}")
    print("="*60)
    print(f"\nReady for circular_pupil_map.py!")
    print(f"GitHub: https://github.com/oscriptcollective/O.IRIS")


def main():
    parser = argparse.ArgumentParser(
        description='O.Iris: Extract EEG metrics for pupil map visualization'
    )
    parser.add_argument('--input', '-i', required=True,
                        help='Input EEG file (BDF, EDF, SET, or FIF)')
    parser.add_argument('--output', '-o', required=True,
                        help='Output CSV file path')
    parser.add_argument('--subject', '-s', type=int, default=1,
                        help='Subject ID (default: 1)')
    parser.add_argument('--window', '-w', type=float, default=10.0,
                        help='Window duration in seconds (default: 10)')
    parser.add_argument('--step', type=float, default=None,
                        help='Step between windows in seconds (default: window size)')

    args = parser.parse_args()
    step = args.step if args.step else args.window

    print("\n" + "="*60)
    print("O.Iris: EEG Metrics Extraction")
    print("The Mind's Eye Has an Iris")
    print("="*60)
    print(f"Input:   {args.input}")
    print(f"Output:  {args.output}")
    print(f"Subject: {args.subject}")
    print(f"Window:  {args.window}s | Step: {step}s")
    print(f"Phi-seam focal value: m = {PHI_M}")
    print("="*60 + "\n")

    df = process_file(args.input, args.subject, args.window, step)

    if len(df) == 0:
        print("ERROR: No valid windows extracted.")
        return

    df.to_csv(args.output, index=False)
    print(f"\nSaved {len(df)} windows to: {args.output}")
    print_summary(df)


if __name__ == '__main__':
    main()