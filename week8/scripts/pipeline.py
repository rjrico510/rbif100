#!/usr/bin/env python3
"""Pipeline to take a gene name, and get sequence/homolog infomation.

Given a gene name & species:
(1) Get the Ensembl ID from mygene.info
(2) Get the sequence data:
(2a) Use the Ensembl ID to get the gene's DNA sequence from Ensembl
(2b) Find the longest open reading frame and convert to an amino acid sequence
(2c) Write the results of the above steps to a fasta file
(3) Get species with homologous genes and write to a file.

inputs:
(1) Gene name
(2) Species (currently only homo sapiens is supported)

outputs:
(1) A fasta of the gene sequence and the AA sequence of the longest open reading frame
(2) A homolog file containing a sorted list of all other species with homologous genes
"""

import argparse
import Bio.Seq
import logging
import json
import pathlib
import re
import requests
import sys
import typing

LOGGER = logging.getLogger(__name__)  # logger for entire module

SPECIES = {
    "homo sapiens":
    {
        "mygene": "human",
        "ensembl": "homo_sapiens"
    }
}


class OutputFiles(typing.NamedTuple):
    """output files"""

    fasta_file: pathlib.Path
    homolog_file: pathlib.Path


def parse_arguments() -> argparse.Namespace:
    """parse arguments

    Returns:
        argparse.Namespace: argument object
    """

    DEFAULT_OUTPUT_DIR = "."
    DEFAULT_SPECIES = "homo sapiens"
    LOG_DEFAULT = "pipeline.log"

    parser = argparse.ArgumentParser(
        description="Given a human gene name, get the sequence, AA of longest open reading frame, and homologs"
    )
    parser.add_argument("gene_name", help="gene name")
    parser.add_argument(
        "-s", "--species", choices=SPECIES.keys(), default=DEFAULT_SPECIES, help=f"species (default {DEFAULT_SPECIES})"
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        dest="output_dir",
        default=DEFAULT_OUTPUT_DIR,
        help=f"output folder (default {DEFAULT_OUTPUT_DIR})",
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
    LOGGER.info(f"Gene name: {args.gene_name}")
    LOGGER.info(f"Species: {args.species}")
    LOGGER.info(f"Output directory: {args.output_dir}")
    LOGGER.info(f"Force overwrite: {args.force}")
    LOGGER.info(f"Verbose: {args.verbose}")
    LOGGER.info(f"Log file: {args.logfile}")

    return args


def setup_outputs(gene_name: str, output_dir: str, force: bool = False) -> OutputFiles:
    """setup output paths and verify

    Args:
        gene_name (str): gene name
        output_dir (str): output directory
        force (bool, optional): override if files already exists.   Defaults to False.

    Returns:
        OutputFiles: tuple of fasta and homolog files
    """
    FASTA_FILENAME_ROOT = "_gene_AA.fasta"
    HOMOLOG_FILENAME_ROOT = "_homology_list.txt"
    fasta_file = pathlib.Path(output_dir, f"{gene_name}{FASTA_FILENAME_ROOT}")
    homolog_file = pathlib.Path(output_dir, f"{gene_name}{HOMOLOG_FILENAME_ROOT}")

    output_files = OutputFiles(fasta_file=fasta_file, homolog_file=homolog_file)

    pathlib.Path(output_dir).mkdir(exist_ok=True, parents=True)

    for output_file in output_files:
        if pathlib.Path.exists(output_file):
            if force:
                LOGGER.info(f"{output_file} exists - will overwrite")
            else:
                LOGGER.error(f"{output_file} already exists - exiting...")
                sys.exit(1)

    return output_files


def get_ensembl_gene_id(
    name: str, species: str, output_dir: str, verbose: bool = False
) -> str:
    """Get ensembl ID from mygene.info.
       Exits if not found.

    Args:
        name (str): gene name
        species (str): species
        output_dir (str): output directory (only used with verbose)
        verbose (bool, optional): More verbose output.   Defaults to False.

    Returns:
        str: Ensembl ID
    """

    url = "https://mygene.info/v3/query"
    params = {"q": name, "species": [SPECIES[species]["mygene"]], "fields": "symbol,name,ensembl,taxid"}
    data = _request(url, params, verbose)

    if verbose:
        with pathlib.Path(output_dir, "mygene.json").open(mode="w") as f:
            json.dump(data, f, indent=4)

    if data.get("hits") and len(data["hits"]) > 0:  # must be a hit - get the 1st
        try:
            ensembl_gene_id = data["hits"][0]["ensembl"]["gene"]
        except KeyError:
            LOGGER.error(f"MyGeneInfo - no ensembl gene ID found - exiting...")
            sys.exit(1)
    else:
        print(f"No hits for {name} - exiting...")
        sys.exit(1)

    return ensembl_gene_id


def get_fasta(
    ensembl_gene_id: str, fasta_file: pathlib.Path, output_dir: str, verbose: bool = False
) -> None:
    """Get gene sequence
       Get longest open reading frame in the sequence and convert to an AA sequence
       Write both to a fasta file

    Args:
        ensembl_gene_id (str): Ensembl gene ID
        fasta_file (pathlib.Path): fasta file to write to
        output_dir (str): output directory (only used with verbose)
        verbose (bool, optional): More verbose output.   Defaults to False.
    """

    # get the sequence data
    url = f"https://rest.ensembl.org/sequence/id/{ensembl_gene_id}"
    params = {"content-type": "application/json", "type": "genomic"}
    data = _request(url, params, verbose)

    if verbose:
        with pathlib.Path(output_dir, "ensembl_gene.json").open(mode="w") as f:
            json.dump(data, f, indent=4)

    # translate the longest open reading frame to an AA sequence
    orf = Bio.Seq.Seq(_get_longest_orf_aa(data["seq"]))
    aa = orf.translate()
    LOGGER.debug(aa)

    # write the fasta
    with fasta_file.open(mode="w") as f:
        f.write(f">{data['desc']}\n")
        f.write(f"{data['seq']}\n")
        f.write(f">{ensembl_gene_id}:longest_ORF:AA\n")
        f.write(f"{str(aa)}\n")


def get_homologs(
    ensembl_gene_id: str, species: str, homolog_file: pathlib.Path, output_dir: str, verbose: bool = False
) -> None:
    """Get list of species which are homologous to a specified gene

    Args:
        ensembl_gene_id (str): Ensembl Gene ID
        species (str): species
        homolog_file (pathlib.Path): output file
        output_dir (str): output directory (only used with verbose)
        verbose (bool, optional): More verbose output.   Defaults to False.
    """
    url = f"https://rest.ensembl.org/homology/id/{ensembl_gene_id}"
    params = {
        "content-type": "application/json",
        "layout": "condensed",
        "sequence": "none",
    }
    data = _request(url, params, verbose)

    if verbose:
        with pathlib.Path(output_dir, "ensembl_homolog.json").open(mode="w") as f:
            json.dump(data, f, indent=4)

    # identify all the unique species specified - sort & write out
    homologous_species = set()
    if data.get("data") and len(data["data"]) > 0:
        for homology in data["data"][0].get("homologies", []):
            homologous_species.add(homology["target"]["species"])
    else:
        LOGGER.warning("No homology data for {ensembl_gene_id}")
    
    species_ensembl = SPECIES[species]["ensembl"]
    if species_ensembl in homologous_species:
        homologous_species.remove(species_ensembl)  # omit the species you're looking at (if present)

    homologous_species = list(homologous_species)
    homologous_species.sort()

    with homolog_file.open(mode="w") as f:
        for s in homologous_species:
            f.write(f"{s}\n")


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


def _request(url: str, params: dict = None, verbose: bool = False) -> dict:
    """Executes a request.    Exit if the request fails.

    Args:
        url (str): URL for the request
        params (dict, optional): Dictionary of query parameters. Defaults to None.
        verbose (bool, optional): More verbose output.   Defaults to False.

    Returns:
        dict: json output of the response.
    """
    response = requests.get(url, params=params)
    if response.status_code not in (200, 301):
        LOGGER.error(f"API call failure: {url} - response code {response.status_code}")
        sys.exit(1)

    data = response.json()
    return data


def _get_longest_orf_aa(dna: str) -> str:
    """Get longest open reading frame in a DNA strand

    Args:
        dna (str): DNA transcript

    Returns:
        str: AA of longest open reading frame.  None if not found.
    """
    regex = re.compile(r"ATG(?:[ACTG]{3})*?(?:TAA|TAG|TGA)")
    hits = regex.findall(dna)
    if hits:
        longest = max(hits, key=len)
        LOGGER.debug(len(longest))
        LOGGER.debug(longest)
    else:
        longest = None

    return longest


def main():
    """main"""
    args = parse_arguments()
    LOGGER.info("-- Setup output --")
    output = setup_outputs(args.gene_name, args.output_dir, args.force)

    LOGGER.info("-- get ensembl ID from mygene.info --")
    ensembl_gene_id = get_ensembl_gene_id(
        args.gene_name, args.species, args.output_dir, args.verbose
    )
    LOGGER.info(f"Ensembl ID: {ensembl_gene_id}")

    LOGGER.info("-- get nucleotide sequence via Ensembl --")
    LOGGER.info("-- translate longest open reading frame to AA --")
    LOGGER.info("-- write to fasta --")
    get_fasta(ensembl_gene_id, output.fasta_file, args.output_dir, args.verbose)

    LOGGER.info("-- get homologous genes via Ensembl --")
    get_homologs(ensembl_gene_id, args.species, output.homolog_file, args.output_dir, args.verbose)
    LOGGER.info("-- END ANALYSIS --")


if __name__ == "__main__":
    main()
