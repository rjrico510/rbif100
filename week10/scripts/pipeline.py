#!/usr/bin/env/python3
"""Pipeline to take a clinical data file, folder of diversity & distance information for each sample
and generate
(1) mean/standard deviation data for each sample
(2) scatter plots and for the distance data for the top N and lowest M average diversity samples
(default N=2, M=1)
(3) K-means plots for (2)

inputs:
(1) clinical data file:
- Tab-delimited file with the following headers
Discoverer	Location	Diamater (mm)	Environment	Status	code_name
(2) folder of diversity scores
- file names within the folder: <code_name>.diversity.txt
- text files with a single column of values; no header
- all files have the same # data points
(3) folder of distance scores
- file names within the folder: <code_name>.distance.txt
- csv files with two columns; no header

outputs:
(1) updated clinical data file with averages, std for each entry.
(2) Scatter plots of the distance data for the top N and bottom M average diversities
(3) K-means cluster plots of the same data from (2)
"""

import argparse
import glob
import logging
import numpy as np
import os
import pandas as pd
import sys

LOGGER = logging.getLogger(__name__)  # logger for entire module


def parse_arguments() -> argparse.Namespace:
    """parse arguments

    Returns:
        argparse.Namespace: argument object
    """

    DEFAULT_MAX_AVE = 2
    DEFAULT_MIN_AVE = 1
    DEFAULT_NEW_CLINICAL_DATA = "clinical_data_with_diversity.txt"
    DEFAULT_OUTPUT_DIR = "."
    LOG_DEFAULT = "pipeline.log"

    parser = argparse.ArgumentParser(
        description="Given clinical data, diversity and distance data, compute mean/std dev and generate scatter plots"
    )
    parser.add_argument("clinical_data_file", help="clinical data file")
    parser.add_argument("diversity_dir", help="directory of diversity scores")
    parser.add_argument("distances_dir", help="directory of distances data")
    parser.add_argument(
        "-m", "--min", default=DEFAULT_MIN_AVE, type=int, help=f"number of lowest average samples to plot (default {DEFAULT_MIN_AVE})"
    )
    parser.add_argument(
        "-n", "--max", default=DEFAULT_MAX_AVE, type=int, help=f"number of highest average samples to plot (default {DEFAULT_MAX_AVE})"
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        dest="output_dir",
        default=DEFAULT_OUTPUT_DIR,
        help=f"output folder (default {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "-c",
        "--clinical-data-output",
        dest="clinical_data_output",
        default=DEFAULT_NEW_CLINICAL_DATA,
        help=f"new clinical data file name for output directory (default {DEFAULT_NEW_CLINICAL_DATA})",
    )
    parser.add_argument(
        "-f", "--force", action="store_true", help="force overwrite of existing output"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="verbose - more logging and outputs",
    )
    parser.add_argument("-l", "--logfile", help=f"log file name (default {LOG_DEFAULT})", default=LOG_DEFAULT)
    args = parser.parse_args()

    #
    # setup log file
    #
    print(f"Logging to {args.logfile} with verbosity: {args.verbose}")
    _setup_logger(args.verbose, args.logfile)

    LOGGER.info("-- START ANALYSIS --")
    LOGGER.info("-- Parse and validate input --")

    # echo inputs
    LOGGER.info(f"Clinical Data file (input): {args.clinical_data_file}")
    LOGGER.info(f"Diversity directory (input): {args.diversity_dir}")
    LOGGER.info(f"Distances directory (input): {args.distances_dir}")
    LOGGER.info(f"Output directory: {args.output_dir}")
    LOGGER.info(f"New clinical data file: {args.clinical_data_output}")
    LOGGER.info(f"Force overwrite: {args.force}")
    LOGGER.info(f"Verbose: {args.verbose}")
    LOGGER.info(f"Log file: {args.logfile}")

    return args


def setup_inputs_outputs(input_clinical_file: str, diversity_dir: str, distances_dir: str, output_dir: str, output_clinical_file: str, force: bool=False) -> str:
    """configure and validate input/output

    Args:
        input_clinical_file (str): input clinical data file (can be a path)
        diversity_dir (str): input diversity directory
        distances_dir (str): input distances directory
        output_dir (str): output directory
        output_clinical_file (str): output clinical file name within output directory
        force (bool, optional): Overwrite existing data. Defaults to False.

    Returns:
        str: full path to clinical data output file based on inputs
    """

    # is the input present?
    missing_input = False
    for input in (input_clinical_file, diversity_dir, distances_dir):
        if not os.path.exists(input):
            LOGGER.error(f"Missing input: {input}")
    if missing_input:
        sys.exit(1)

    # are the directories really directories?
    not_dir = False
    for input in (diversity_dir, distances_dir):
        if not os.path.isdir(input):
            LOGGER.error(f"Not a directory: {input}")
    if not_dir:
        sys.exit(1)

    output_clinical_filepath = os.path.join(output_dir, output_clinical_file)

    # create the output dir; exit if previous results are present unless overridden
    if os.path.exists(output_dir):
        if not force and os.path.exists(output_clinical_filepath):
            LOGGER.error(f"output is already present - use --force to overwrite")
            sys.exit(1)
    else:
        os.makedirs(output_dir)

    # don't overwrite the original clinical file
    LOGGER.debug(f"Input clinical data: {os.path.realpath(input_clinical_file)}")
    LOGGER.debug(f"Output clinical data: {os.path.realpath(output_clinical_filepath)}")
    if os.path.realpath(input_clinical_file) == os.path.realpath(output_clinical_filepath):
        LOGGER.error("input and output clinical files map to the same file - exiting to avoid overwriting")
        sys.exit(1)

    # return the clinical output file full path
    return output_clinical_filepath


def generate_diversity_stats(clinical_data_file: str, diversity_dir: str, clinical_data_output: str, output_dir: str=None, verbose: bool=False) -> pd.DataFrame:
    """Generate mean/std dev for each diversity data set and add to clinical data to create a new file

    Args:
        clinical_data (str): input clinical file
        diversity_dir (str): input directory of diversity files
        clinical_data_output (str): output clinical file
        output_dir (str, optional): output for any additional reporting.   Required if verbose=True.   Defaults to None.
        verbose (bool, optional): Write additional logging information. Defaults to False.

    Returns:
        pd.DataFrame: clinical data plus statistical data as a dataframe
    """

    if verbose and output_dir is None:
        raise ValueError("If verbose is set, you must specify output_dir")

    DIVERSITY_FILENAME_ROOT = ".diversity.txt"

    clinical_data = pd.read_csv(clinical_data_file, sep="\t")
    clinical_data.set_index("code_name", drop=False, inplace=True)
    clinical_data.sort_index(ascending=True, inplace=True) # Q: do I even need this?
    LOGGER.debug("-- clinical data input --")
    LOGGER.debug(clinical_data)

    # read all the diversity files into a dataframe
    diversity_filenames = [f for f in os.listdir(diversity_dir) if f.endswith(DIVERSITY_FILENAME_ROOT)]
    #diversity_filenames.sort()
    diversity_data = pd.DataFrame()
    for diversity_filename in diversity_filenames:
        code_name = diversity_filename.split(".")[0]
        diversity_data[code_name] = pd.read_csv(os.path.join(diversity_dir, diversity_filename), header=None)
    LOGGER.debug("-- diversity data input --")
    LOGGER.debug(diversity_data)

    diversity_mean = diversity_data.mean()
    diversity_std = diversity_data.std()

    LOGGER.debug("-- mean --")
    LOGGER.debug(diversity_mean)
    LOGGER.debug("-- std dev --")
    LOGGER.debug(diversity_std)

    if verbose:
        diversity_mean.to_csv(os.path.join(output_dir, "diversity_mean.csv"))
        diversity_std.to_csv(os.path.join(output_dir, "diversity_std.csv"))

    clinical_data["averages"] = diversity_mean
    clinical_data["std"] = diversity_std

    LOGGER.debug("-- clinical data output --")
    LOGGER.debug(clinical_data)

    clinical_data.to_csv(clinical_data_output, sep="\t", index=False, float_format='%.3f')

    return clinical_data


#
# helper code
#


def _setup_logger(debug: bool, logfile: str) -> None:
    """set up logger

    Set up a handler for both a log file and stdout/stderr

    Args:
        debug (bool): if level should be set to debug
        logfile (str): log file name.
    """
    log_dir = os.path.dirname(logfile)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    LOGGER.setLevel(logging.DEBUG)  # base level

    level = logging.DEBUG if debug else logging.INFO

    # stream handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    LOGGER.addHandler(handler)

    # file handler
    handler = logging.FileHandler(logfile)
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s: %(message)s"))
    LOGGER.addHandler(handler)


def main():
    """main
    # read in clinical_data.txt as a pandas dataframe
    # - create 2 new columms (averages & std dev)
    # for each diversity file
    # - read in, append mean/stddev (use pandas/numpy)
    # find top 2 & lowest 1 average diversity
    # - for these 3, generate scatter plot from distance file
    # EC - perform k-means clustering on the 3 plots & color by cluster (use elbow method to determine # clusters)
    """
    args = parse_arguments()
    LOGGER.info("-- Setup input/output --")
    clinical_output_file = setup_inputs_outputs(args.clinical_data_file, args.diversity_dir, args.distances_dir, args.output_dir, args.clinical_data_output, args.force)
    LOGGER.info("-- Generate Diversity Statistics --")
    clinical_data = generate_diversity_stats(args.clinical_data_file, args.diversity_dir, clinical_output_file, args.output_dir, args.verbose)

if __name__ == "__main__":
    main()