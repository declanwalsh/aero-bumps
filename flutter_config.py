# -*- coding: utf-8 -*-
"""
General (non-analysis specific) configuration files
@author: dek_work
"""

# !!!!!!!!!!!!!!!!!!!!!!!!
# load configuration file in the /config directory here
# !!!!!!!!!!!!!!!!!!!!!!!!
from config import config_DAQ11270_000009 as cfg_analysis

DEBUG = False # shows debugging data for program printed in console (not vibration data)
SHOW_DETAIL = True # shows additional vibration data

FILTER_DAMPING = True # filters data 
CALC_DAMPING = True # calculates damping
CALC_FREQ = True # calculate peak frequencies from FFT

PLOT_FFT = True # plots the FFT
PLOT_DATA = True # plots the actual data

CHECK_STAT = False # checks some statistical measures on data (stationary)

SAVE_FIG = True # saves all plotted figures to png in the working directory
SAVE_OUTPUT = True # saves frequencies in a csv

# Folder relative to program
# TODO - automatically generate folders if they are not already present in the directory
CSV_FILE_ROOT = "Data/" # input CSV's
IMAGE_FILE_ROOT = "Images/" # output images
OUTPUT_FILE_ROOT = "Results/" # output csv summaries
FILTERED_IMAGE_FILE_ROOT = "Filtered/"

# matplotlib figure sizes in inches
FIGURE_WIDTH = 8
FIGURE_HEIGHT = 5
LIMITS = [-1.5, 3]

# standard high order for Butterworth filters
FILTER_ORDER = 4

# columns in numpy array for storing data in program memory
COL_IDX = 0
COL_TIME = 1
COL_SIGNAL = 2
COL_FILTERED = 3

COL_PRESSURE = 2
COL_TEMP = 3
COL_ALT = 4

# columns in output csv
COL_OUT_SOURCE = 0
COL_OUT_TEST = 1
COL_OUT_FREQ = 2
COL_OUT_DAMPING = 3
COL_OUT_DAMPING_FREQ = 4