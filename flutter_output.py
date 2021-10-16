# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 10:09:36 2020

TODO
- Add spectrogram of changes in modal frequencies at different airspeeds
"""

from mpl_toolkits.mplot3d import Axes3D

import csv
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

import flutter_config as cfg
from flutter_config import cfg_analysis

import bisect

#---------------------------------
# FUNCTIONS - COMPARE RESULTS
#---------------------------------

def compare_data_acc(results):
    
    plot_modal_variation_with_airspeed(results, [10, 24])
    plot_modal_variation_with_airspeed(results, [30])
    
    plot_modal_variation_with_airspeed_3D(results, 10, [280, 290, 300, 310, 320, 330, 340, 350])
    plot_modal_variation_with_airspeed_3D(results, 24, [330, 340, 350])
    plot_modal_variation_with_airspeed_3D(results, 30, [0.68, 0.70, 0.72, 0.74, 0.76, 0.78, 0.80, 0.81])
    
    if cfg.CALC_DAMPING:
        plot_damping_variation_with_airspeed(results, [10, 24])
        plot_damping_variation_with_airspeed(results, [30])   
    
    return 1

def plot_damping_variation_with_airspeed(results, altitude_list, title = None, subtitle = None):
 
    fig, ax = plt.subplots()
    min_airspeed = 1000
    max_airspeed = 0
    altitude_str = ""
    
    for altitude in altitude_list:
        for idx in range(len(cfg_analysis.FREQ_FILTER_MODE)):
            modal_damping_results, modal_airspeed_results = get_damping_variation_with_airspeed(results, altitude, idx)
            
            print(modal_damping_results)
            print(modal_airspeed_results)
            
            if not modal_airspeed_results or not modal_damping_results: # case where no modes were detected for frequency and empty list returned
                print("No modes for {}".format(cfg_analysis.FREQ_FILTER_MODE[idx]))
                continue

            min_airspeed = min(min(modal_airspeed_results), min_airspeed)
            max_airspeed = max(max(modal_airspeed_results), max_airspeed)

            label_str = "{:.1f}".format(cfg_analysis.FREQ_FILTER_MODE[idx]) + " Hz (nom.) @ " + str(altitude) + "K"

            ax.plot(modal_airspeed_results, modal_damping_results, label = label_str, marker = "*") #  marker='o'

        altitude_str = "_" + altitude_str + str(altitude) + "K"

    ax.plot([0, 1000], [-0.03, -0.03], linestyle='--', color='red', label = "Limit")
            
    plt.ylabel("Structural Damping")
    
    if max_airspeed < 2:
        plt.xlabel("Mach Number")
    else:
        plt.xlabel("Airspeed (KIAS)")
            
    if title is None:
        str_title = "Damping Variation"
        
    plt.suptitle(str_title, fontsize=20, y = 1)
    
    if subtitle is None:
       subtitle = cfg_analysis.ACC_BASIS_STR
        
    plt.title(subtitle, fontsize=16)
    
    tick_spacing = 0.03
        
    ax.legend()  
    ax.set_xlim([min_airspeed,max_airspeed])
    ax.set_ylim([-0.18, 0])
    ax.yaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
    fig.set_size_inches(cfg.FIGURE_WIDTH, cfg.FIGURE_HEIGHT)      
    plt.show()
    
    if cfg.SAVE_FIG:
        fig.savefig(cfg.IMAGE_FILE_ROOT + cfg_analysis.ANALYSIS_FILE_ROOT + cfg_analysis.ACC_BASIS_STR + "_DAMPING" + altitude_str + ".png")

def plot_modal_variation_with_airspeed(results, altitude_list, title = None, subtitle = None):
 
    fig, ax = plt.subplots()
    min_airspeed = 1000
    max_airspeed = 0
    altitude_str = ""
    
    for altitude in altitude_list:
        for modal_freq in cfg_analysis.FREQ_FILTER_MODE:
            modal_freq_results, modal_airspeed_results = get_modal_variation_with_airspeed(results, altitude, modal_freq)
            
            if not modal_airspeed_results or not modal_freq_results: # case where no modes were detectec for frequency and empty list returned
                print("No modes for {}".format(modal_freq))
                continue
            
            min_airspeed = min(min(modal_airspeed_results), min_airspeed)
            max_airspeed = max(max(modal_airspeed_results), max_airspeed)
            
            label_str = "{:.1f}".format(modal_freq) + " Hz (nom.) @ " + str(altitude) + "K"
            
            ax.plot(modal_airspeed_results, modal_freq_results, label = label_str, marker = "*") #  marker='o'
            
        altitude_str = "_" + altitude_str + str(altitude) + "K"

    plt.ylabel("Frequency (Hz)")
    
    if max_airspeed < 2:
        plt.xlabel("Mach Number")
    else:
        plt.xlabel("Airspeed (KIAS)")
            
    if title is None:
        str_title = "Modal Frequency Variation"
        
    plt.suptitle(str_title, fontsize=20, y = 1)
    
    if subtitle is None:
       subtitle = cfg_analysis.ACC_BASIS_STR
        
    plt.title(subtitle, fontsize=16)
        
    ax.legend()  
    ax.set_xlim([min_airspeed,max_airspeed])
    ax.set_ylim([0, 10])
    fig.set_size_inches(cfg.FIGURE_WIDTH, cfg.FIGURE_HEIGHT)      
    plt.show()
       
    if cfg.SAVE_FIG:
        fig.savefig(cfg.IMAGE_FILE_ROOT + cfg_analysis.ANALYSIS_FILE_ROOT + cfg_analysis.ACC_BASIS_STR + "_FREQUENCY" + altitude_str + ".png")
   
def plot_modal_variation_with_airspeed_3D(results, altitude, airspeed_values, title = None, subtitle = None):
    
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    max_freq = 12
    
    f_big = []
    Gxx_big = []
    airspeed_big = []
    
    altitude_str = "_" + str(altitude) + "K"
        
    for airspeed in airspeed_values:
        f, Gxx = get_freq_variation_with_airspeed(results, altitude, airspeed, max_freq)
        
        if len(f) > 0:
            airspeed_list = [airspeed]*len(f)
            f_big.extend(f)
            airspeed_big.extend(airspeed_list)
            Gxx_big.extend(Gxx)
            ax.plot(f, airspeed_list, Gxx)
    
    ax.set_ylim(min(airspeed_values), max(airspeed_values))
    ax.set_xlim(0, max_freq)
    
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Airspeed')
    ax.set_zlabel('Amplitude')
    
    if title is None:
        plt.suptitle("Modal Frequency Variation @ " + str(altitude) + "K", fontsize=20, y = 1)

    fig.set_size_inches(cfg.FIGURE_WIDTH, cfg.FIGURE_HEIGHT)   

    plt.draw()
    
    if cfg.SAVE_FIG:
        fig.savefig(cfg.IMAGE_FILE_ROOT + cfg_analysis.ANALYSIS_FILE_ROOT + cfg_analysis.ACC_BASIS_STR + "_FREQUENCY_3D_line" + altitude_str + ".png")

    
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # surface expects a regular 2D grid structure
    # colourmaps = https://matplotlib.org/3.1.0/tutorials/colors/colormaps.html
    ax.plot_trisurf(f_big, airspeed_big, Gxx_big, cmap="plasma", antialiased=True)
    
    ax.set_ylim(min(airspeed_values), max(airspeed_values))
    ax.set_xlim(0, max_freq)
    
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Airspeed')
    ax.set_zlabel('Amplitude')

    if title is None:
        plt.suptitle("Modal Frequency Variation @ " + str(altitude) + "K", fontsize=20, y = 1)

    fig.set_size_inches(cfg.FIGURE_WIDTH, cfg.FIGURE_HEIGHT)   
    
    plt.draw()

    if cfg.SAVE_FIG:
        fig.savefig(cfg.IMAGE_FILE_ROOT + cfg_analysis.ANALYSIS_FILE_ROOT + cfg_analysis.ACC_BASIS_STR + "_FREQUENCY_3D_shaded" + altitude_str + ".png")

    return fig, ax

def get_freq_variation_with_airspeed(results, altitude, airspeed, max_freq):
    
    f = []
    Gxx = []
    
    for test_point in results:
        if test_point["altitude"] == altitude and test_point["airspeed"] == airspeed:
            f_results = test_point["f"]
            Gxx_results = test_point["Gxx"]
            
            f = f_results
            Gxx = Gxx_results
            
            idx_max_freq = bisect.bisect(f, max_freq)
            f = f[:idx_max_freq]
            Gxx = Gxx[:idx_max_freq]
    
    return f, Gxx

def get_damping_variation_with_airspeed(results, altitude, modal_freq_idx):
    
    damping_ratio = []
    modal_airspeed = []
    
    for test_point in results:
        if test_point["altitude"] == altitude:
            
                damping_ratio_results = test_point["damping_modal_ratio"]
            
                damping_ratio.append(-2*damping_ratio_results[modal_freq_idx])
                modal_airspeed.append(test_point["airspeed"])
            
    return damping_ratio, modal_airspeed
     
def get_modal_variation_with_airspeed(results, altitude, modal_freq_of_interest):
    
    modal_freq = []
    modal_airspeed = []
    
    for test_point in results:
        if test_point["altitude"] == altitude:
            
            modal_freq_match = get_closest_match(test_point["modal_freq"], modal_freq_of_interest, cfg_analysis.FREQ_FILTER_VARIATION)
            
            if modal_freq_match is not None:
                modal_freq.append(modal_freq_match)
                modal_airspeed.append(test_point["airspeed"])
            
    return modal_freq, modal_airspeed

"""
Returns the closest value in a list to a target within a limit
Returns none if no values in the list are within the limit to the target
"""
def get_closest_match(data, target, limit):
    
    closest = None
    
    # TODO - this might be able to be skipped over more efficiently
    min_difference = abs(target - limit)
    
    for value in data:
        difference = abs(value - target)
        if difference < min_difference and difference < limit:
            min_difference = difference
            closest = value
        
    return closest

#---------------------------------
# FUNCTIONS - PLOTTING
#---------------------------------

# damping and airspeed should be array of arrays
# each array is a different flight profile
def plot_value_variation_with_airspeed(airspeed, data, legend_str, title_str):
    
 #   assert(len(airspeed) == len(damping))
    
    fig, ax = plt.subplots()

    for idx in len(airspeed):
        ax.plot(airspeed[idx], data[idx], label = legend_str[idx])
    

def extract_relevant_value(data_list, acceptable_range):
    
    relevant_value = None
    
    for value in data_list:
        if value >= acceptable_range[0] and value <= acceptable_range[1]:
            if relevant_value is None:
                relevant_value = value
            else:   
                print("More than one value in the data list falls within range - returning None")
                return None

    return relevant_value

"""
Plots simple histogram of data
"""
def plot_histogram(data):

    plt.hist(data, bins='auto')  # arguments are passed to np.histogram
    plt.title("Histogram of data")
    plt.ylabel("Counts in sample")
    plt.xlabel("Signal (automatically binned)")
    plt.show()
 
"""
Plots the frequency domain of the signal
"""
# TODO - make this handle maximum values nicer
def welch_plot(f, Gxx, f_max, Gxx_max, title = None, subtitle = None):
    
    fig, ax = plt.subplots()
    ax.plot(f, Gxx, label = "Signal") #  marker='o'
    ax.set_xlim([0,50])

    #ax.set_yscale('log')
    #ax.set_ylim([10**-4,10**2])    
    plt.ylabel("Relative strength")
    plt.xlabel("Frequency (Hz)")
    
    if title is None:
        str_title = "PSD of Data"
    else:
        str_title = "PSD of " + title
        
    plt.suptitle(str_title, fontsize=20, y = 1)
    
    if subtitle is not None:
        plt.title(subtitle, fontsize=16)
        
    plt.plot(f_max, Gxx_max, "x", label = "Peaks")
    ax.legend(loc='upper right')  
    fig.set_size_inches(cfg.FIGURE_WIDTH, cfg.FIGURE_HEIGHT)      
    plt.show()
    
  
        
    if cfg.SAVE_FIG:
        fig.savefig(cfg.IMAGE_FILE_ROOT + cfg_analysis.ANALYSIS_FILE_ROOT + title + "_FREQ" + ".png")
    
"""
plots time varying data using Matplotlib
"""
def plot_acc(data, time, title = None, peaks_idx = None, fileref = None, subtitle = None, limits = None, save_image = True, filtered_image = False):
    
    # TODO - colour extracted section different (to accout for the 1 second on either side)
    fig, ax = plt.subplots()
    ax.plot(time, data, label = "Signal")
    plt.ylabel("Signal (V or g's)")
    plt.xlabel("Time (s)")
    if title is None:
        plt.suptitle("Signal Variation with Time (raw)")
        title = fileref
    else:
        plt.suptitle("Signal of " + title, fontsize=20, y = 1)
        
    if subtitle is not None:
        if filtered_image:
             plt.title("Filtered between: " + subtitle + " (Hz)", fontsize=16)
        else:
             plt.title(subtitle, fontsize=16)
        
    if peaks_idx is not None:
        ax.plot(time[peaks_idx[0]], data[peaks_idx[0]], "x", label = "Identified peaks")
        for i in list(range(len(peaks_idx[0]))):
          ax.annotate(i, (time[peaks_idx[0][i]], data[peaks_idx[0][[i]]]), textcoords = "offset points", xytext = (0,10), ha = "center")

    if limits is not None:
        ax.set(ylim=limits)
        
    ax.legend(loc='upper right')  
    fig.set_size_inches(cfg.FIGURE_WIDTH, cfg.FIGURE_HEIGHT)      
    
    plt.show()
    
    if cfg.SAVE_FIG and save_image:
        if filtered_image:
            fig.savefig(cfg.IMAGE_FILE_ROOT + cfg_analysis.ANALYSIS_FILE_ROOT + cfg.FILTERED_IMAGE_FILE_ROOT + title + subtitle + "_FILTERED" + ".png")
        else:
            fig.savefig(cfg.IMAGE_FILE_ROOT + cfg_analysis.ANALYSIS_FILE_ROOT + title + "_TIME" + ".png")

    return plt

"""
    Plots atmosphere data from test data
    Overlays on a vibration profile (if one is provided) or creates new graph (if none is provided)
"""
def plot_atmosphere(altitude, time, temperature=None, fig=None, fileref=None):

    if fig is None:
        fig, ax = plt.subplots()

    ax.plot(time, altitude, label = "Altitude")
    plt.ylabel("Pressure Altitude (ft)")
    plt.xlabel("Time (s)")
    
    return None

#---------------------------------
# FUNCTIONS - CSV
#---------------------------------

"""
saves the data out as a csv
saves in rows instead of columns as easier to work with
"""
def save_csv_output(data, filename):
    
    print(f"Saving csv with data to {filename}.csv")
    
    filename_complete = cfg.OUTPUT_FILE_ROOT + filename + ".csv"
    with open(filename_complete, mode='w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for cols in data:
            csv_writer.writerow(cols)
            
    print("CSV saved.")
        
    return 1