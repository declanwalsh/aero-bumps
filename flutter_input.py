# -*- coding: utf-8 -*-
"""flutter_input

Generates python-compatible data from raw measured data.

Converts the input data into numpy arrays. Input data is normally in the form of csv's.

  Typical usage example:

  foo = ClassFoo()
  bar = foo.FunctionBar()

TODO
- None
"""

# ---------------------------------
# IMPORTS
# ---------------------------------

from datetime import datetime
import numpy as np
import re
import sys

import flutter_config as cfg
from flutter_config import cfg_analysis

from flutter_other import stationary_check, acc_filter_butter
from flutter_output import plot_acc, plot_atmosphere, plot_histogram

from atmosphere import altitude_from_height

# ---------------------------------
# CONSTANTS
# ---------------------------------

# keys are the regex strings to be matched
# values are the string time python format
TIME_FORMAT_DICT = {}

# Format: 28/11/2019 10:46:01.099 AM
TIME_FORMAT_DICT.update({r"\d{1}\/\d{2}\/\d{4} \d{1}:\d{2}:\d{2}\.\d{3} (AM|PM)$":"%d/%m/%Y %H:%M:%S.%f %p"})

# Format: 42:36.335
TIME_FORMAT_DICT.update({r"\d{2}:\d{2}.\d{3}$":"%M:%S.%f"})

# Format: 36.335
TIME_FORMAT_DICT.update({r"\d{2}.\d{3}$":"%S.%f"})

# conversion factor for V to mV
V_TO_MV = 1000

# ---------------------------------
# FUNCTIONS
# ---------------------------------


def import_data_acc(analysis_files, idx_file):
    """Imports and preprocesses accelereometer data"""

    acc_data = import_csv_acc(analysis_files[idx_file], cfg_analysis.DATA_FORMAT)

    # butterworth filter doesn't do much here
    # most daq's and accelerometers have inbuilt low pass filters
    # data_filter = acc_data[:, cfg.COL_SIGNAL]
    data_filter = acc_filter_butter(acc_data[:, cfg.COL_SIGNAL], cfg_analysis.FREQ_LOWPASS, 'lowpass')
    acc_data = np.c_[acc_data, data_filter]

    if cfg.SHOW_DETAIL:
        print("\nData overview sample: ")
        print(acc_data)

        _check_timestep(acc_data[:, cfg.COL_TIME])

    if cfg.CHECK_STAT:
        stationary_check(acc_data[:, cfg.COL_SIGNAL],
                         acc_data[:, cfg.COL_TIME],
                         check_autocorr=False)

        # plotting histrograms may be very slow for large datasets
        plot_histogram(acc_data[:, cfg_analysis.COL_SIGNAL])

    if cfg.PLOT_DATA:

        print("\nPlotting entire raw accelerometer data range")

        if cfg_analysis.DATA_FORMAT == 0:
            fileref = cfg_analysis.ACC_BASIS_STR + " " + analysis_files[idx_file].split(".")[0] + " RAW "
        elif cfg_analysis.DATA_FORMAT == 1:
            fileref = cfg_analysis.ACC_BASIS_STR + "_TOTAL"

        plot_acc(data=acc_data[:, cfg.COL_SIGNAL],
                 time=acc_data[:, cfg.COL_TIME],
                 fileref=fileref)

    return acc_data


def import_data_atmos(analysis_files, idx_file):
    """Imports and preprocesses atmospheric data"""

    atmos_data = import_csv_atmos(analysis_files[idx_file], cfg_analysis.DATA_FORMAT)

    if cfg.PLOT_DATA:

        print("\nPlotting entire raw atmospheric data range")

        if cfg_analysis.DATA_FORMAT == 0:
            fileref = cfg_analysis.ACC_BASIS_STR + " " + analysis_files[idx_file].split(".")[0] + " RAW "
        if cfg_analysis.DATA_FORMAT == 1:
            fileref = cfg_analysis.ACC_BASIS_STR + "_TOTAL"

        plot_atmosphere(altitude=atmos_data[:, cfg.COL_ALT],
                        time=atmos_data[:, cfg.COL_TIME],
                        fileref=fileref)

    return atmos_data


# ---------------------------------
# FUNCTIONS - CSV IMPORT
# ---------------------------------


def import_csv_acc(filename, data_format):
    """Imports accelerometer data from csv"""

    # Endevco 7257AT data
    # https://buy.endevco.com/contentstore/mktgcontent/endevco/datasheet/7257at_ds_091819.pdf
    if data_format == 0:
        # import from csv
        acc_data_raw = np.genfromtxt(cfg.CSV_FILE_ROOT + filename, delimiter=",",
                                     dtype='unicode', skip_header=cfg_analysis.NUM_HEADER_ROWS)
        # remove leading and trailing quotation marks if present
        acc_data_cleaned = np.char.strip(acc_data_raw, "\"")

        # extract columns from csv
        sample_conv = acc_data_cleaned[:, cfg_analysis.COL_IDX_MEASURE].astype(int)
        time_basis = acc_data_cleaned[:, cfg_analysis.COL_TIME_MEASURE]
        time_format = _identify_time_format(time_basis[1])
        # convert time from string to float
        time_conv = _convert_times(time_basis, time_format)
        voltage_conv = acc_data_cleaned[:, cfg_analysis.COL_SIGNAL_MEASURE].astype(float)

        # remove the DC bias offset
        # 2.5 DC bias specified in datasheet - this gets an average of approximately 0.7g
        voltage_conv = voltage_conv - np.mean(voltage_conv)
        acc_conv = voltage_conv * cfg_analysis.CALIBRATION * V_TO_MV

        # form numpy array
        acc_data_conv = np.transpose(np.array([sample_conv, time_conv, acc_conv]))

    # Slam Stick or Endaq data
    elif data_format == 1:
        # import from csv
        acc_data_raw = np.genfromtxt(cfg.CSV_FILE_ROOT + filename, delimiter=",",
                                     dtype='float', skip_header=cfg_analysis.NUM_HEADER_ROWS)
        time_basis = acc_data_raw[:, cfg_analysis.COL_TIME_MEASURE]
        acc_conv = acc_data_raw[:, cfg_analysis.COL_SIGNAL_MEASURE]
        sample_conv = np.array(range(len(acc_data_raw)))

        # form numpy array
        acc_data_conv = np.transpose(np.array([sample_conv, time_basis, acc_conv]))

    else:
        print("In function import_csv_acc...")
        sys.exit("ERROR - INVALID FILE FORMAT SELECTED")

    if cfg.DEBUG:
        print(acc_data_conv)

    return acc_data_conv


def import_csv_atmos(filename, data_format):

    if data_format == 0:
        # endveco data has no atmospheric data
        atmos_data_conv = None

    # Slam Stick or Endaq data
    elif data_format == 1:
        # import from csv
        atmos_data_raw = np.genfromtxt(cfg.CSV_FILE_ROOT + filename, delimiter=",",
                                       dtype='float', skip_header=cfg_analysis.NUM_HEADER_ROWS)
        time_basis = atmos_data_raw[:, cfg_analysis.COL_TIME_MEASURE]
        pressure_conv = atmos_data_raw[:, cfg_analysis.COL_PRESSURE_MEASURE]
        alt_conv = altitude_from_height(pressure_conv, "Pa")
        temp_conv = atmos_data_raw[:, cfg_analysis.COL_TEMP_MEASURE]
        sample_conv = np.array(range(len(atmos_data_raw)))

        # form numpy array
        atmos_data_conv = np.transpose(np.array([sample_conv, time_basis, pressure_conv, temp_conv, alt_conv]))

    else:
        print("In function import_csv_atmos...")
        sys.exit("ERROR - INVALID FILE FORMAT SELECTED")

    if cfg.DEBUG:
        print(atmos_data_conv)

    return atmos_data_conv


# ---------------------------------
# FUNCTIONS - MISC
# ---------------------------------


def _convert_times(data, time_format):
    """converts string of times to float of seconds since time started"""

    if time_format is None:
        print("ERROR - time_format_idx must be defined, no valid time string match found")
        sys.exit()

    time_basis = np.zeros(data.size)

    print(data)

    time_start = datetime.strptime(data[0], time_format)

    for idx in range(1, len(data)):
        tmp_conv = datetime.strptime(data[idx], time_format)
        time_conv = tmp_conv - time_start
        time_conv = time_conv.seconds + time_conv.microseconds*1e-6
        time_basis[idx] = time_conv

    return time_basis


# ---------------------------------
# FUNCTIONS - CHECKS - INPUT
# ---------------------------------


def _check_config_file():

    no_errors = True

    if len(cfg_analysis.CSV_FILE) != len(cfg_analysis.TIME_EXTRACT):
        print(f"ERROR - There are {len(cfg_analysis.CSV_FILE)} files and {len(cfg_analysis.TIME_EXTRACT)} different file times")
        print("Check CSV_FILE and TIME_EXTRACT")
        no_errors = False

    if len(cfg_analysis.CSV_FILE) != len(cfg_analysis.ALTITUDE):
        print(f"ERROR - There are {len(cfg_analysis.CSV_FILE)} files and {len(cfg_analysis.ALTITUDE)} different altitudes")
        print("Check CSV_FILE and ALTITUDE")
        no_errors = False

    if len(cfg_analysis.CSV_FILE) != len(cfg_analysis.AIRSPEED):
        print(f"ERROR - There are {len(cfg_analysis.CSV_FILE)} files and {len(cfg_analysis.AIRSPEED)} different airspeeds")
        print("Check CSV_FILE and AIRSPEED")
        no_errors = False

    if len(cfg_analysis.TIME_EXTRACT[0]) != len(cfg_analysis.ALTITUDE[0]):
        print(f"ERROR - There are {len(cfg_analysis.TIME_EXTRACT[0])} time slices and {len(cfg_analysis.ALTITUDE[0])} different altitudes")
        print("Check CSV_FILE and TIME_EXTRACT")
        no_errors = False

    if len(cfg_analysis.TIME_EXTRACT[0]) != len(cfg_analysis.AIRSPEED[0]):
        print(f"ERROR - There are {len(cfg_analysis.TIME_EXTRACT[0])} time slices and {len(cfg_analysis.AIRSPEED[0])} different airspeeds")
        print("Check CSV_FILE and ALTITUDE")
        no_errors = False

    if no_errors:
        return 1
    else:
        print("Invalid inputs in analysis config file")
        print("Stopping program now...")
        sys.exit()


def _check_timestep(time):
    """Checks the timesteps between adjacent elements in a vector of times"""
    print("\nChecking timesteps...")

    difference = np.diff(time)
    max_diff = np.max(difference)
    min_diff = np.min(difference)
    av_diff = np.mean(difference)

    print(f"Max. timestep: {max_diff:.5f}")
    print(f"Min. timestep: {min_diff:.5f}")
    print(f"Average timestep: {av_diff:.5f}")
    print(f"Timestep used in analysis: {cfg_analysis.TIMESTEP:.5f}")
    print("NOTE: FFT assumes equal timesteps between all points. Differences may introduce errors.")


def _identify_time_format(str_sample_time):
    """Checks which format the time string in the csv is in and returns time format"""

    time_format = None

    for regex_pattern_string in TIME_FORMAT_DICT:
        regex_pattern = re.compile(regex_pattern_string)

        if regex_pattern.search(str_sample_time):
            time_format = TIME_FORMAT_DICT[regex_pattern_string]

        if cfg.DEBUG:
            print(f"Checking time format of string: {str_sample_time}")
            if time_format is None:
                print(f"ERROR - no valid time_format found for regex pattern: {regex_pattern_string}")
            else:
                print("SUCCESS - valid time format found")
                print(f"Regex of {regex_pattern_string}")

        print(f"Time format is {time_format} (Regex of {regex_pattern_string})")

    return time_format
