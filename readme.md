# bumps
*bumps* is a program for analysing vibration data and is specifically aimed at data from flight testing.

## Description
There are several files in the program:
- flutter_analysis: Runs numerical analysis on the dataset including frequency and damping calculations.
- flutter_config: Specifies analysis configuration and loads dataset configuration file
- flutter_main: Top level program that is run by user to start the analysis.
- flutter_other: Additional mathematical functions.
- flutter_output: Renders figures and graphs of the results.
- specific config file: Config files are kept in the /config folder and are specific to a dataset to account for differences. There are example config files that are commented and should be used as a starting point.

# Use
To use the program:
1. Export the dataset file into a csv from your accelerometer. For endaq/slam stick acceleometers use the enDAQ lab program from [here](https://endaq.com/pages/vibration-shock-analysis-software-endaq-slam-stick-lab). 
1. Move the dataset csv into the data folder.
1. Create a suitable configuration file
1. Update flutter_config.py as required (make sure to load the new configuration file)
1. Run flutter_main.py
1. Results are shown in the console and saved in /Images and /Results folders

# Libraries
```
source ~/venv/venv_aerobumps/activate/bin
```

# Issues
In case of bugs, ask Declan.