# -*- coding: utf-8 -*-
"""



TODO
- Add calculation of damping with the half-point power method
"""

#---------------------------------
# IMPORTS
#---------------------------------

import math
import numpy as np
import scipy.signal as signal
import sys

import flutter_config as cfg
from flutter_config import cfg_analysis

from flutter_other import stationary_check, acc_filter_butter
from flutter_output import plot_acc, welch_plot

#---------------------------------
# FUNCTIONS
#---------------------------------

def analyse_data_acc(acc_data, time_ranges, idx_range, airspeed, altitude, subtitle):

    dict_results = {"altitude": altitude, "airspeed": airspeed}

    data_extract, data_raw_extract, time_extract = extract_time_and_data(acc_data, time_ranges, idx_range)

    if airspeed is None:
        str_title = cfg_analysis.ACC_BASIS_STR + " " + str(altitude)  
    elif airspeed < 2:
        str_title = cfg_analysis.ACC_BASIS_STR + " " + str(altitude) + "KM" + str(airspeed)
    else:
        str_title = cfg_analysis.ACC_BASIS_STR + " " + str(altitude) + "K" + str(airspeed)
        
    str_subtitle = "Flight Test Conditions: " + subtitle
                            
    print(f"\n\nStarting analysis for {str_title}")
            
    if cfg.PLOT_DATA:
        print("\nPlotting filtered data range")
        plot_acc(data = data_extract, time = time_extract, title = str_title, subtitle = str_subtitle, limits = cfg.LIMITS)
 
    f_max = None
    if cfg.CALC_FREQ:
        f_max, f, Gxx = analyse_data_freq(data_extract, time_extract, str_title, str_subtitle)
        
    dict_results["modal_freq"] = f_max

    # modal frequency data for use in plotting later
    dict_results["f"] = f
    dict_results["Gxx"] = Gxx
    
    damping_modal_ratio = None
    if cfg.CALC_DAMPING:
        damping_modal_ratio = analyse_data_damping(data_extract, data_raw_extract, time_extract, str_title)
    dict_results["damping_modal_ratio"] = damping_modal_ratio
    # TODO Change the name of these
    dict_results["f_modal"] = cfg_analysis.FREQ_FILTER_MODE
    
    if cfg.DEBUG:
        print("Results for analysis are:")
        print(dict_results)
    
    return dict_results

def extract_time_and_data(acc_data, time_ranges, idx_range):
    
    if time_ranges[idx_range] != 0:
        
        if cfg_analysis.DATA_FORMAT == 0:
            sys.exit(f"ERROR - DATA_FORMAT and TIME_RANGES mismatch")

        times = time_ranges[idx_range]

        time_lower = times[0] - cfg_analysis.OFFSET
        time_upper = times[1] + cfg_analysis.OFFSET

        idx_start = min(np.where(acc_data[:, cfg.COL_TIME] > time_lower)[0])
        idx_end = max(np.where(acc_data[:, cfg.COL_TIME] < time_upper)[0])
        time_extract = acc_data[:, cfg.COL_TIME][idx_start:idx_end]
        data_extract = acc_data[:, cfg.COL_FILTERED][idx_start:idx_end]
        data_raw_extract = acc_data[:, cfg.COL_SIGNAL][idx_start:idx_end]
        
    else:

        time_extract = acc_data[:, cfg.COL_TIME]
        data_extract = acc_data[:, cfg.COL_FILTERED]
        data_raw_extract = acc_data[:, cfg.COL_SIGNAL]

    if cfg.CHECK_STAT:
        stationary_check(data_extract, time_extract, check_mean = False)
        
    return data_extract, data_raw_extract, time_extract
                 
def analyse_data_freq(data_extract, time_extract, str_title, str_subtitle):
    
    samp_freq = cfg_analysis.SAMP_RATE
                        
    f_max, f, Gxx = welch_calc(data = data_extract, samp_freq = samp_freq, time = time_extract, title = str_title, subtitle = str_subtitle)
    print(f"Peak frequencies for {str_title} are {np.round(f_max,2)}Hz")
    print("Refer to graph to verify all detected peaks")
                
    return f_max, f, Gxx
    
# TODO - review if this needs to be the raw data
def analyse_data_damping(data_extract, data_raw_extract, time_extract, str_title):
    
    damping_modal_ratio = []

    if cfg.FILTER_DAMPING:
        
        if len(cfg_analysis.FREQ_FILTER_REF) == 0:
            low_freq_filter = float(input("Enter low frequency for band-pass filter: "))
            high_freq_filter = float(input("Enter high frequency for band-pass filter: "))
            freq_filter = [[low_freq_filter, high_freq_filter]]
            
        else:
            freq_filter = cfg_analysis.FREQ_FILTER_REF
            print(f"Filtering between: {freq_filter} Hz")
            
        for idx in range(len(freq_filter)):
            str_damp_subtitle = str(freq_filter[idx])
            filtered_data_extract = acc_filter_butter(data = data_raw_extract, freq = freq_filter[idx], filter_type = 'bandpass')
            damping_modal_ratio.append(calc_damping_ratio_log_dec(data = filtered_data_extract - np.mean(filtered_data_extract), time = time_extract,  title = str_title, subtitle = str_damp_subtitle))


    else:
        damping_modal_ratio.append(calc_damping_ratio_log_dec(data = data_extract - np.mean(data_extract), time = time_extract,  title = str_title))
        
    if damping_modal_ratio is not []:
        print(f"Damping ratio from logarithmic decrement method for identified mode in {str_title} is {damping_modal_ratio}")
        
    return damping_modal_ratio

#---------------------------------
# FUNCTIONS - FREQUENCY ANALYSIS
#---------------------------------



"""
estimate the power spectral density (signal relative power at different frequencies)
uses a Fourier transform method
"""
# TODO - time unused currently, may be used in case of unequal time spacing in future
def welch_calc(data, time, samp_freq, title = None, subtitle = None):
    
    print("\nEstimating power spectral density using Welch's method...")
    
    #window_1 = 2^13;
    #overlap_1 = 2^11;
    #freq_res_1 = SAMP_RATE/window_1
    
    # main magic here
    # https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.signal.welch.html
    # https://docs.scipy.org/doc/scipy/reference/signal.windows.html?highlight=window#module-scipy.signal.windows
    [f, Gxx] = signal.welch(x = data, fs = samp_freq, nperseg = cfg_analysis.BIN_SIZE, window='hann')
    
    if cfg.SHOW_DETAIL:
        print(f"Length of data sample is {len(data)}")
        print(f"Frequency step in FFT: {f[1] - f[0]:.2f}Hz")
    
    max_idx = signal.find_peaks(Gxx, height = cfg_analysis.PEAK_THRESHOLD*max(Gxx))
    f_max = f[max_idx[0]]
    Gxx_max = Gxx[max_idx[0]]
    
    if cfg.PLOT_FFT:    
        welch_plot(f, Gxx, f_max, Gxx_max, title, subtitle)
    
    return f_max, f, Gxx

#---------------------------------
# FUNCTIONS - DAMPING ANALYSIS
#---------------------------------

"""
calculate the damping ratio by logarithmic decremenet for an underdamped system
more effective for SDOF system as MDOF system have free decay from multiple modes
only valid for damping ratio < 1 and less accurate for damping ratio > 0.5
"""
def calc_damping_ratio_log_dec(data, time, title = None, subtitle = None):
    
    max_idx = signal.find_peaks(data, height = 0.25*max(data), distance = 20)

    plot_acc(data = data, time = time,  title = title, peaks_idx = max_idx, subtitle = subtitle, save_image = True, filtered_image = True)

    print("Starting logarithmic decrement method of determing damping ratio...")    
    #print("!!WARNING!! - Ill suited to MDOF systems such as an aircraft wing")
    #print("System has free decay from multiple modes at different damping")
    #print("Half power point method preferred if sufficient frequency resolution")

    damp_ratio = None

    if len(max_idx[0]) > 1:

        max_idx_of_group = np.argmax(data[max_idx[0]])

        if cfg_analysis.DAMPING_AUTOMATIC is True:
            check_graph = "Y"
        else:
            check_graph = input("Manually check for damping ratio from graph (y/n/(o)ther side) (default: y): ") or "y"

        if check_graph.upper()[0] == "O":
            repeat_flipped = input("Check from other side (flips graph to negative and repeats) (y/n) (default: n): ") or "n"
            if repeat_flipped.upper()[0] == "Y":
                damp_ratio = calc_damping_ratio_log_dec(-1*data, time, title)

        elif check_graph.upper()[0] != "N" :
    
            print(f"{len(max_idx[0])} peaks found")
            print("Avoid the inital impulse for this calculation")
            
            
            if cfg_analysis.DAMPING_AUTOMATIC is True:
                idx_1 = max_idx_of_group
                idx_2 = len(max_idx[0]) - 1
                num_cycles = idx_2 - idx_1
                print(f"Automatically detecting max/min peaks as {idx_1} and {idx_2} over {num_cycles} cycles")
            else:
                idx_1 = input(f"Enter peak number to be inital peak (integer only - first peak is 0 - defaults to max value {max_idx_of_group}):\n") or max_idx_of_group
                idx_1 = validate_log_dec_peak_selection(idx_1, max_idx[0])
                idx_2 = input(f"Enter peak number to be later peak (integer only - first peak is 0 - defaults to last peak {len(max_idx[0]) - 1}):\n") or len(max_idx[0]) - 1
                idx_2 = validate_log_dec_peak_selection(idx_2, max_idx[0])
                num_cycles = input(f"Enter number of successive peaks between selected peaks (integer only - 1 if adjacent - default {idx_2 - idx_1}): ") or (idx_2 - idx_1)
                num_cycles = int(num_cycles)
            
            log_dec = (1/num_cycles)*math.log(data[max_idx[0][idx_1]]/data[max_idx[0][idx_2]])
            damp_ratio = 1/math.sqrt(1 + (2*math.pi/log_dec)**2)
            
            if cfg.DEBUG:
                print(damp_ratio)
        
    else:
        print("Skipping damping calc for datapoint - less than two peaks detected")

    return damp_ratio


"""
checks that user input damping peak indicies are valid and coverts them to integers
"""
def validate_log_dec_peak_selection(idx, ref_idx):
    
    idx_corr = int(idx)
    
    if idx_corr < 0 or idx_corr > len(ref_idx) - 1:
        print("ERROR - invalid damping index selected")
        print(f"There are {len(ref_idx)} peaks only (starting from 0 NOT 1)")
        print(f"You entered {idx}, which was interpreted as {idx_corr}")
        sys.exit()
    
    return idx_corr