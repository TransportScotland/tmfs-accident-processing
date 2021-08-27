# tmfs-accident-processing
Python code for undertaking accident analysis on TMfS outputs

## Usage
In many circumstances, the executable version of this application should be used - in particular, using this directly within Cube allows for accident analysis via `PILOT`, rather than the hassle of setting up a Python environment for use as a Custom User Program in Cube.

Calling the executable from the command line with the `-h` / `--help` flag will display a short help message, shown below:

```text
usage: tmfs-accident-processing_v0.0.1.exe [-h] rates_workbook network_file year log_file output_csv

Apply accident calculations for a single network.

positional arguments:
  rates_workbook  Accident rates workbook
  network_file    Network file to process
  year            Year of the network
  log_file        Output log file for the process
  output_csv      Output CSV file for the results

optional arguments:
  -h, --help      show this help message and exit
```

## Input files

### `rates_workbook`
This should be an excel workbook containing the accident rates to be applied, with relevant requirements on sheet and column names met. **The full path (including drive and folders) should be provided.**

_Naming requirements and example workbook coming soon_

### `network_file`
This network should be an exported DBF of the network, with a column called `ANN_V` containing the annualised vehicle volume for every link. **The full path (including drive and folders) should be provided.**

### `year`
The year the provided network corresponds to. Should be in 4-digit form, e.g. `2021`, and should be passed as a number, not a string (be careful with Cube keys!)

## Output files

### `log_file`
The process writes some text outputs to a text-based log file for records and potentially debugging - provide a file path for the logs to go into. **The full path (including drive and folders) should be provided.**

### `csv_file`
The main output of the process is a CSV file containing the accident and casualty numbers calculated for the provided parameters - provide a file path for the output to go into. **The full path (including drive and folders) should be provided.**

## Example `PILOT` script
```shell
*"{CATALOG_DIR}\executables\tmfs-accident-processing_v0.0.1.exe" "{Accident Rates Workbook}" "{SCENARIO_DIR}\{Scenario_ShortName} Annualised Network.dbf" {Year} "{SCENARIO_DIR}\Analysis.log" "{SCENARIO_DIR}\{Scenario_ShortName}_Accident Summary.csv"
```

This assumes:
1. The executable is stored alongside the catalog file in a folder called `Executables`
2. The required network file has been created (likely in a `NETWORK` box in the previous step) and saved as `{SCENARIO_DIR}\{Scenario_ShortName} Annualised Network.dbf`
3. `Year` is a catalog key, with type set to integer
4. `Accident Rates Workbook` is a catalog key (likely Filename type, but could be string), set to "Output Value as specified", i.e.:

![Cube "edit key" window, with the "Advanced" button highlighted](images/Cube_Edit-Key-Page.png)
![Cube "Advanced Key Settings" window, with the "Output Value as specified" button highlighted](images/Cube_Advanced-key-settings.png)