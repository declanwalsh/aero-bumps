# -*- coding: utf-8 -*-
"""Main runtime program for analysis

TODO
- Signal is very weak, it should be more distinct on a log scale
- Pod accelerometer data (not slam sticks) have too similar main frequencies (possible processing artifact or measurement issue)
- May need to correct for the accelerometer mounting having damping, etc.
"""

# Data is required to be:
# - Equal timesteps between each datapoint

import flutter_config as cfg
from flutter_config import cfg_analysis

from flutter_input import import_data_acc, import_data_atmos, check_config_file
from flutter_analysis import analyse_data_acc
from flutter_output import compare_data_acc, save_csv_output


def main_program():
    """Main runtime"""

    check_config_file()

    analysis_files = cfg_analysis.CSV_FILE

    analysis_files_atmos = cfg_analysis.CSV_FILE_ATMOS

    print(f"Running on {analysis_files_atmos[0]}...")
    atmos = import_data_atmos(analysis_files, 0)

    out_data = [["Source"], ["Test"], ["Frequencies"], ["Damping"], ["Damping Frequencies (Ref.)"]]

    # for every file
    for idx_file in range(len(analysis_files)):

        airspeed = cfg_analysis.AIRSPEED[idx_file]
        altitude = cfg_analysis.ALTITUDE[idx_file]
        time_ranges = cfg_analysis.TIME_EXTRACT[idx_file]
        subtitle = cfg_analysis.SUBTITLE[idx_file]

        print(f"Running on {analysis_files[idx_file]}...")
        acc_data = import_data_acc(analysis_files, idx_file)

        results = []

        # for every time range in the file
        for idx_range in range(len(time_ranges)):

            result_test_point = analyse_data_acc(acc_data, time_ranges, idx_range,
                                                 airspeed[idx_range], altitude[idx_range], subtitle[idx_range])

            # by setting airspeed to None in testpoints, they can be removed from data result processing
            if airspeed[idx_range] is not None:
                results.append(result_test_point)

            if cfg.SAVE_OUTPUT:
                out_data[cfg.COL_OUT_SOURCE].append(cfg_analysis.ACC_BASIS_STR)
                title_core = str(result_test_point["airspeed"]) + " @ " + str(result_test_point["altitude"]) + "K"
                out_data[cfg.COL_OUT_TEST].append(title_core)
                if cfg.CALC_FREQ:
                    out_data[cfg.COL_OUT_FREQ].append(result_test_point["modal_freq"])
                if cfg.CALC_DAMPING:
                    out_data[cfg.COL_OUT_DAMPING].append(result_test_point["damping_modal_ratio"])
                    out_data[cfg.COL_OUT_DAMPING_FREQ].append(result_test_point["f_modal"])

    compare_data_acc(results)

    save_csv_output(out_data, cfg_analysis.ACC_BASIS_STR)


if __name__ == "__main__":
    main_program()
