# -*- coding: utf-8 -*-
"""flutter_other

Miscellaneous functions for analysis
"""

import math
import matplotlib as plt
import numpy as np
import scipy.signal as signal
import sys

import flutter_config as cfg
from flutter_config import cfg_analysis


def acc_filter_butter(data, freq, filter_type):
    """Apply butterworth filter to data"""

    filter_order = cfg.FILTER_ORDER = 4

    if filter_type == 'bandpass' or filter_type == 'bandstop':
        if len(freq) != 2:
            sys.exit(f"ERROR - Frequency length must be two for bandpass/bandstop filters (Current length: {len(freq)})")
        freq_filter = [f/(cfg_analysis.SAMP_RATE/2) for f in freq]
    elif filter_type == 'lowpass' or filter_type == 'high_pass':
        freq_filter = freq/(cfg_analysis.SAMP_RATE/2)
    else:
        sys.exit(f"ERROR - Invalid filter format selected (Filter selected: {filter_type})")

    """Using b/a filter in Scipy with Nyquist frequency much larger than filter frequency has issues from from float numerical precision
    sos (second order sections representation of IIR filter) fixes these issue
    """
    # [b,a] = signal.butter(FILTER_ORDER, freq_filter, filter_type);
    # data_filter = signal.filtfilt(b, a, data)
    sos = signal.butter(filter_order, freq_filter, filter_type, output="sos")
    data_filter = signal.sosfiltfilt(sos, data)

    return data_filter

# ---------------------------------
# FUNCTIONS - CHECKS - STATISTICAL
# ---------------------------------


def stationary_check_mean(data):
    """Checks if data is stationary by getting variation of mean over time"""
    tmp_len = len(data)
    NUM_SEGMENTS = 10
    num_points = math.floor(tmp_len/NUM_SEGMENTS)

    data_stat = np.zeros([NUM_SEGMENTS, num_points])

    for idx in range(NUM_SEGMENTS):
        data_stat[idx, :] = data[idx*num_points:(idx+1)*num_points]

    data_mean = np.mean(data_stat, axis=1)

    diff_mean = max(data_mean) - min(data_mean)
    diff_total = max(data) - min(data)
    diff_ratio = diff_mean/diff_total

    if cfg.SHOW_DETAIL:
        print(f"\nVariation in mean is {diff_ratio*100:.2f}% of total variation")

    return data_mean


def stationary_check_autocorrelation(data):
    """Checks if data is stationary by getting variation of autocorrelation over time"""

    tmp_len = len(data)
    NUM_SEGMENTS = 3
    num_points = math.floor(tmp_len/NUM_SEGMENTS)

    autocorr_norm = np.zeros([NUM_SEGMENTS, num_points-1])

    for idx in range(NUM_SEGMENTS):

        x = data[idx*num_points:(idx+1)*num_points]

        x = x - x.mean()

        autocorr = np.correlate(x, x, mode='full')
        autocorr = autocorr[x.size:]

        # normalise the data
        autocorr /= autocorr.max()

        autocorr_norm[idx, :] = autocorr

    lag = cfg_analysis.TIMESTEP*np.arange(0, num_points)

    return autocorr_norm, lag[:-1]


def stationary_check(data, time, check_mean=True, check_autocorr=True):
    """Check if data is weakly stationary by plotting variation in mean and autocorrelation over time"""

    if check_mean:

        data_mean = stationary_check_mean(data)
        plot_mean_variation_with_time(time, data_mean)

    if check_autocorr:

        [data_corr, lag] = stationary_check_autocorrelation(data)
        plot_autocorr_variation_with_time(lag, data_corr)


def plot_mean_variation_with_time(time, data_mean):
    """Plots variation of mean over time
    Used to check for stationary data
    Minimal variation over time for stationary data
    """

    plt.plot(np.linspace(time[0], time[-1], len(data_mean)), data_mean)
    plt.title('Variation of Mean over Time')
    plt.xlabel('Time (s)')
    plt.ylabel('Mean of Data over segment')
    plt.show()


def plot_autocorr_variation_with_time(lag, data_corr):
    """Plots variation of autocorrelation over time
    Used to check for stationary data
    Peaks should match for stationary data
    """

    fig, ax = plt.subplots()

    for idx_corr in range(len(data_corr)):
        ax.plot(lag, data_corr[idx_corr, :], label="Sec. " + str(idx_corr))

    # ax.set_xlim([0, 1])
    plt.xlabel('Lag (s)')
    plt.ylabel('Normalised Correlation')
    plt.title('Autocorrelation Variation over Time')
    ax.legend()
    plt.show()
