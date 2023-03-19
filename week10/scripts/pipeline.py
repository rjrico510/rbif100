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
import logging
import matplotlib
import matplotlib.backends.backend_pdf as backend_pdf
import matplotlib.pyplot as plt
import numpy as np
import pathlib
import pandas as pd
import scipy.spatial.distance as sp_distance
import seaborn as sns
import sklearn.cluster
import sys
import typing

LOGGER = logging.getLogger(__name__)  # logger for entire module


class InputFiles(typing.NamedTuple):
    """input files"""

    clinical_file: pathlib.Path
    diversity_dir: pathlib.Path
    distances_dir: pathlib.Path


class OutputFiles(typing.NamedTuple):
    """output files"""

    clinical_file: pathlib.Path
    output_dir: pathlib.Path


def parse_arguments() -> argparse.Namespace:
    """parse arguments

    Returns:
        argparse.Namespace: argument object
    """

    DEFAULT_NUM_HIGH = 2
    DEFAULT_NUM_LOW = 1
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
        "-m",
        "--num-low",
        dest="num_high",
        default=DEFAULT_NUM_LOW,
        type=int,
        help=f"number of lowest average samples to plot (default {DEFAULT_NUM_LOW})",
    )
    parser.add_argument(
        "-n",
        "--num-high",
        dest="num_low",
        default=DEFAULT_NUM_HIGH,
        type=int,
        help=f"number of highest average samples to plot (default {DEFAULT_NUM_HIGH})",
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
    parser.add_argument(
        "-l",
        "--logfile",
        help=f"log file name (default {LOG_DEFAULT})",
        default=LOG_DEFAULT,
    )
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
    LOGGER.info(f"Number high average to plot: {args.num_high}")
    LOGGER.info(f"Number low average to plot: {args.num_low}")
    LOGGER.info(f"Force overwrite: {args.force}")
    LOGGER.info(f"Verbose: {args.verbose}")
    LOGGER.info(f"Log file: {args.logfile}")

    return args


def setup_inputs_outputs(
    input_clinical_file: str,
    diversity_dir: str,
    distances_dir: str,
    output_dir: str,
    output_clinical_file: str,
    force: bool = False,
) -> tuple:
    """configure and validate input/output

    Args:
        input_clinical_file (str): input clinical data file (can be a path)
        diversity_dir (str): input diversity directory
        distances_dir (str): input distances directory
        output_dir (str): output directory
        output_clinical_file (str): output clinical file name within output directory
        force (bool, optional): Overwrite existing data. Defaults to False.

    Returns:
        tuple: (InputFiles, OutputFiles)
    """

    # is the input present?
    missing_input = False
    for input in (input_clinical_file, diversity_dir, distances_dir):
        if not pathlib.Path(input).exists():
            LOGGER.error(f"Missing input: {input}")
    if missing_input:
        sys.exit(1)

    # are the directories really directories?
    not_dir = False
    for input in (diversity_dir, distances_dir):
        if not pathlib.Path(input).is_dir():
            LOGGER.error(f"Not a directory: {input}")
    if not_dir:
        sys.exit(1)

    output_clinical_filepath = pathlib.Path(output_dir, output_clinical_file)

    # create the output dir; exit if previous results are present unless overridden
    if pathlib.Path(output_dir).exists():
        if not force and output_clinical_filepath.exists():
            LOGGER.error(f"output is already present - use --force to overwrite")
            sys.exit(1)
    else:
        pathlib.Path(output_dir).mkdir(parents=True)

    # don't overwrite the original clinical file
    real_input_clinical_file = pathlib.Path(input_clinical_file).resolve()
    real_output_clinical_file = output_clinical_filepath.resolve()
    LOGGER.debug(f"Input clinical data: {real_input_clinical_file}")
    LOGGER.debug(f"Output clinical data: {real_output_clinical_file}")
    if real_input_clinical_file == real_output_clinical_file:
        LOGGER.error(
            "input and output clinical files map to the same file - exiting to avoid overwriting"
        )
        sys.exit(1)

    # return the clinical output file full path
    inputs = InputFiles(
        clinical_file=real_input_clinical_file,
        diversity_dir=pathlib.Path(diversity_dir),
        distances_dir=pathlib.Path(distances_dir),
    )
    outputs = OutputFiles(
        clinical_file=real_output_clinical_file, output_dir=pathlib.Path(output_dir)
    )
    return (inputs, outputs)


def generate_diversity_stats(
    clinical_data_file: pathlib.Path,
    diversity_dir: pathlib.Path,
    clinical_data_output: pathlib.Path,
    output_dir: pathlib.Path = None,
    verbose: bool = False,
) -> pd.DataFrame:
    """Generate mean/std dev for each diversity data set and add to clinical data to create a new file

    Args:
        clinical_data (pathlib.Path): input clinical file
        diversity_dir (pathlib.Path): input directory of diversity files
        clinical_data_output (pathlib.Path): output clinical file
        output_dir (pathlib.Path, optional): output for any additional reporting.   Required if verbose=True.   Defaults to None.
        verbose (bool, optional): Write additional logging information. Defaults to False.

    Returns:
        pd.DataFrame: clinical data plus statistical data as a dataframe
    """

    if verbose and output_dir is None:
        raise ValueError("If verbose is set, you must specify output_dir")

    DIVERSITY_FILENAME_SUFFIX = ".diversity.txt"
    CLINICAL_INDEX = "code_name"

    # read the clinical data file - index by code name
    clinical_data = pd.read_csv(clinical_data_file, sep="\t")
    clinical_data.set_index(CLINICAL_INDEX, drop=False, inplace=True)
    LOGGER.debug("-- clinical data input --")
    LOGGER.debug(clinical_data)

    # read all the diversity files into a dataframe
    diversity_filenames = [
        f for f in diversity_dir.iterdir() if str(f).endswith(DIVERSITY_FILENAME_SUFFIX)
    ]
    LOGGER.debug(diversity_filenames)
    diversity_data = pd.DataFrame()
    for diversity_filename in diversity_filenames:
        code_name = diversity_filename.parts[-1].split(".")[0]
        diversity_data[code_name] = pd.read_csv(diversity_filename, header=None)
    LOGGER.debug("-- diversity data input --")
    LOGGER.debug(diversity_data)

    # generate stats, add to the dataframe & write the result
    diversity_mean = diversity_data.mean()
    diversity_std = diversity_data.std()

    LOGGER.debug("-- mean --")
    LOGGER.debug(diversity_mean)
    LOGGER.debug("-- std dev --")
    LOGGER.debug(diversity_std)

    if verbose:
        diversity_mean.to_csv(pathlib.Path(output_dir, "diversity_mean.csv"))
        diversity_std.to_csv(pathlib.Path(output_dir, "diversity_std.csv"))

    clinical_data["averages"] = diversity_mean
    clinical_data["std"] = diversity_std

    LOGGER.debug("-- clinical data output --")
    LOGGER.debug(clinical_data)

    clinical_data.to_csv(
        clinical_data_output, sep="\t", index=False, float_format="%.3f"
    )

    return clinical_data


def get_extreme_diversity_samples(
    clinical_data: pd.DataFrame, num_high: int = 2, num_low: int = 1
) -> list:
    """Get extreme samples (high/low diversity averages)

    Args:
        clinical_data (pd.DataFrame): full set of clinical data with average diversity score
        num_high (int, optional): number of highest average scores to plot.   Defaults to 2.
        num_low (int, optional): number of lowest average scores to plot.   Defaults to 1.

    Returns:
        list: sample code names with N highest/M lowest diversity averages
    """
    clinical_data.sort_values("averages", inplace=True, ascending=False)
    clinical_data_to_plot = pd.concat(
        [clinical_data.head(num_high), clinical_data.tail(num_low)]
    )
    clinical_data_to_plot.drop_duplicates(
        inplace=True
    )  # cleanup in case the ranges overlap

    LOGGER.debug("-- clinical data to plot --")
    LOGGER.debug(clinical_data_to_plot)

    return list(clinical_data_to_plot.index)


def generate_plots(
    code_names: list,
    distance_dir: pathlib.Path,
    output_dir: pathlib.Path,
    verbose: bool = False,
) -> None:
    """Generate all plots as PDFs

    Args:
        code_names (list): names of samples to plot
        distance_dir (pathlib.Path): directory of distance data
        output_dir (pathlib.Path): output directory
        verbose (bool, optional): Write additional logging information. Defaults to False.
    """
    DISTANCE_FILE_SUFFIX = ".distance.txt"

    for code_name in code_names:
        LOGGER.info(f"plotting {code_name} ...")
        distance_file = pathlib.Path(distance_dir, f"{code_name}{DISTANCE_FILE_SUFFIX}")
        if not distance_file.exists():
            LOGGER.warning(f"missing distance file: {distance_file} .. skipping plot")
            continue

        distance_data = pd.read_csv(distance_file, header=None, names=["x", "y"])
        LOGGER.debug("-- distance data --")
        LOGGER.debug(distance_data)

        _scatter_plot(code_name, distance_data, output_dir)
        _kmeans_plots(code_name, distance_data, output_dir)


#
# helper code
#


def _scatter_plot(
    code_name: str, distance_data: pd.DataFrame, output_dir: pathlib.Path
) -> None:
    """Generate scatter plot of distance data

    Args:
        code_name (str): code name
        distance_data (pd.DataFrame): distance data for the code name
        output_dir (pathlib.Path): output directory
    """
    matplotlib.use("pdf")  # non-GUI backend
    sns.set(font_scale=0.6, palette="colorblind", style="darkgrid")
    dplot = sns.lmplot(
        data=distance_data,
        x="x",
        y="y",
        fit_reg=False,
        scatter_kws={"s": 10, "linewidths": 0.5},
    )
    dplot.set(title=code_name)
    dplot.tight_layout()
    pdf_metadata = {
        "CreationDate": None
    }  # removing field which makes PDFs non-deterministic
    dplot.savefig(pathlib.Path(output_dir, f"{code_name}.pdf"), metadata=pdf_metadata)
    plt.close()


def _kmeans_plots(
    code_name: str,
    distance_data: pd.DataFrame,
    output_dir: pathlib.Path,
    max_clusters: int = 8,
) -> None:
    """Generate K-means plot of distance data

    Args:
        code_name (str): code name
        distance_data (pd.DataFrame): distance data for the code name
        output_dir (pathlib.Path): output directory
        max_clusters (int, optional): maximum number of clusters (defaults to 8)
    """
    matplotlib.use("pdf")  # non-GUI backend

    subplots = []
    distortions = []  # for elbow plot
    for nclusters in range(1, max_clusters + 1):
        # kmeans clustering
        kmeans = sklearn.cluster.KMeans(nclusters, random_state=0)
        cluster_labels = kmeans.fit_predict(distance_data)

        # https://pythonprogramminglanguage.com/kmeans-elbow-method/
        distortions.append(
            sum(
                np.min(
                    sp_distance.cdist(
                        distance_data.to_numpy(), kmeans.cluster_centers_
                    ),
                    axis=1,
                )
            )
            / distance_data.shape[0]
        )

        # add cluster data for plotting purposes
        distance_data[f"cluster_{nclusters}"] = cluster_labels

        # https://stackoverflow.com/questions/64277625/save-multiple-seaborn-plots-into-one-pdf-file
        sns.set(font_scale=0.6, style="darkgrid")
        _, ax = plt.subplots()
        kplot = sns.scatterplot(
            data=distance_data,
            x="x",
            y="y",
            hue=f"cluster_{nclusters}",
            s=10,
            linewidths=0.5,
            palette="colorblind",
        )
        kplot.set(title=f"{code_name} K-means # clusters: {nclusters}")
        kplot.legend(title="cluster")
        subplots.append(ax)

    # make elbow plot
    sns.set(font_scale=0.6, style="darkgrid")
    _, ax = plt.subplots()
    lplot = sns.lineplot(
        x=range(1, max_clusters + 1),
        y=distortions,
        palette="colorblind",
        marker="s",
        markersize=5,
    )
    lplot.set(title=f"{code_name} elbow plot", xlabel="# clusters", ylabel="distortion")
    subplots.append(ax)

    # write cluster plots + elbow plot
    pdf_metadata = {
        "CreationDate": None
    }  # removing field which makes PDFs non-deterministic
    pdf_file = pathlib.Path(output_dir, f"{code_name}_kmeans.pdf")
    with backend_pdf.PdfPages(pdf_file, metadata=pdf_metadata) as pdf:
        for p in subplots:
            pdf.savefig(p.figure)
    plt.close("all")


def _setup_logger(debug: bool, logfile: str) -> None:
    """set up logger

    Set up a handler for both a log file and stdout/stderr

    Args:
        debug (bool): if level should be set to debug
        logfile (str): log file name.
    """
    log_dir = pathlib.Path(logfile).parent
    pathlib.Path(log_dir).mkdir(exist_ok=True, parents=True)

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
    """main"""
    args = parse_arguments()
    LOGGER.info("-- Setup input/output --")
    (inputs, outputs) = setup_inputs_outputs(
        args.clinical_data_file,
        args.diversity_dir,
        args.distances_dir,
        args.output_dir,
        args.clinical_data_output,
        args.force,
    )
    LOGGER.info("-- Generate Diversity Statistics --")
    clinical_data = generate_diversity_stats(
        inputs.clinical_file,
        inputs.diversity_dir,
        outputs.clinical_file,
        outputs.output_dir,
        args.verbose,
    )
    LOGGER.info("-- Get clinical samples to plot --")
    code_names = get_extreme_diversity_samples(
        clinical_data, args.num_low, args.num_high
    )
    LOGGER.info("-- Generate plots --")
    generate_plots(code_names, inputs.distances_dir, outputs.output_dir, args.verbose)
    LOGGER.info("-- DONE --")


if __name__ == "__main__":
    main()
