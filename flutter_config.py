# -*- coding: utf-8 -*-
"""General (non-analysis specific) configuration files

Split into two separate sections:
- This file (cfg) for general program configurations
- Iimported file (cfg_analysis) for analysis specific configurations (including columns, header rows, etc.).

    - import flutter_config as cfg
    - from flutter_config import cfg_analysis
"""

# -----------------
# load configuration file in the /config directory here
# ------------------
from config import config_DAQ11270_000012 as cfg_analysis

DEBUG = False  # shows debugging data for program printed in console (not vibration data)
SHOW_DETAIL = True  # shows additional vibration data

FILTER_DAMPING = True  # filters data
CALC_DAMPING = False  # calculates damping
CALC_FREQ = True  # calculate peak frequencies from FFT

PLOT_FFT = True  # plots the FFT
PLOT_DATA = False  # plots the actual data

CHECK_STAT = False  # checks some statistical measures on data (stationary)

SAVE_FIG = True  # saves all plotted figures to png in the working directory
SAVE_OUTPUT = True  # saves frequencies in a csv

# Folder relative to program
# TODO - automatically generate folders if they are not already present in the directory
CSV_FILE_ROOT = "Data"  # input CSV's
IMAGE_FILE_ROOT = "Images"  # output images
OUTPUT_FILE_ROOT = "Results"  # output csv summaries
FILTERED_IMAGE_FILE_ROOT = "Filtered"

# matplotlib figure sizes in inches
FIGURE_WIDTH = 8
FIGURE_HEIGHT = 5
LIMITS = [-1.5, 3]

# standard high order for Butterworth filters
FILTER_ORDER = 4

# columns in numpy array for storing vibration data in program memory
COL_IDX = 0
COL_TIME = 1
COL_SIGNAL = 2
COL_FILTERED = 3

# columns in numpy array for storing atmospheric data in program memory
# maintains COL_IDX and COL_TIME as before
# different sample rate to vibration data requires different arrays
COL_PRESSURE = 2
COL_TEMP = 3
COL_ALT = 4

# columns in output csv
COL_OUT_SOURCE = 0
COL_OUT_TEST = 1
COL_OUT_FREQ = 2
COL_OUT_DAMPING = 3
COL_OUT_DAMPING_FREQ = 4
