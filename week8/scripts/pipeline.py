#!/usr/bin/env python3
"""TODO - top-level docstring

"""

import argparse
import Bio.Seq
import logging
import json
import os
import re
import requests
import sys
import typing

LOGGER = logging.getLogger(__name__) # logger for entire module


class OutputFiles(typing.NamedTuple):
    """output files"""
    fasta_file: str
    homolog_file: str


def parse_arguments() -> argparse.Namespace:
    """parse arguments

    Returns:
        argparse.Namespace: argument object
    """

    DEFAULT_OUTPUT_DIR = "."
    DEFAULT_SPECIES = "human"
    LOG_DEFAULT = "pipeline.log"

    parser = argparse.ArgumentParser(description="Given a human gene name, get the sequence, AA of longest open reading frame, and homologs")
    parser.add_argument("gene_name", help="gene name")
    parser.add_argument("-s", "--species", default=DEFAULT_SPECIES, help="species (defau;t human)")
    parser.add_argument("-o", "--output-dir", dest="output_dir", default=DEFAULT_OUTPUT_DIR, help="output folder (default current location)")
    parser.add_argument("-f", "--force", action="store_true",  help="force overwrite of existing output")
    parser.add_argument("-v", "--verbose", action="store_true", help="verbose - more logging and outputs")
    parser.add_argument(
        "-l", "--logfile", help="log file name", default=LOG_DEFAULT
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
    LOGGER.info(f"Gene name: {args.gene_name}")
    LOGGER.info(f"Species: {args.species}")
    LOGGER.info(f"Output directory: {args.output_dir}")
    LOGGER.info(f"Force overwrite: {args.force}")
    LOGGER.info(f"Verbose: {args.verbose}")
    LOGGER.info(f"Log file: {args.logfile}")

    return args


def setup_outputs(gene_name: str, output_dir:str, force: bool=False) -> OutputFiles:
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
    fasta_file = os.path.join(output_dir, f"{gene_name}{FASTA_FILENAME_ROOT}")
    homolog_file = os.path.join(output_dir, f"{gene_name}{HOMOLOG_FILENAME_ROOT}")

    output_files = OutputFiles(fasta_file=fasta_file, homolog_file=homolog_file)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    else:
        for output_file in output_files:
            if os.path.exists(output_file):
                if force:
                    LOGGER.info(f"{output_file} exists - will overwrite")
                else:
                    LOGGER.error(f"{output_file} already exists - exiting...")
                    sys.exit(1)

    return output_files

def get_ensembl_gene_id(name: str, species: str, output_dir:str, verbose: bool=False) -> str:
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
    params = {
        "q": name,
        "species": [species],
        "fields": "symbol,name,ensembl,taxid"
    }
    data = _request(url, params, verbose)

    if verbose:
        with open(os.path.join(output_dir, "mygene.json"), "w") as f:
            json.dump(data, f, indent=4)

    if data.get("hits") and len(data["hits"]) > 0: # must be a hit - get the 1st
        try:
            ensembl_gene_id = data["hits"][0]["ensembl"]["gene"]
        except KeyError:
            LOGGER.error(f"MyGeneInfo - no ensembl gene ID found - exiting...")
            sys.exit(1)
    else:
        print(f"No hits for {name} - exiting...")
        sys.exit(1)
        
    return ensembl_gene_id


def get_fasta(ensembl_gene_id: str, fasta_file: str, output_dir:str, verbose: bool=False) -> None:
    """Get gene sequence
       Get longest open reading frame in the sequence and convert to an AA sequence
       Write both to a fasta file

    Args:
        ensembl_gene_id (str): Ensembl gene ID
        fasta_file (str): fasta file to write to
        output_dir (str): output directory (only used with verbose)
        verbose (bool, optional): More verbose output.   Defaults to False.
    """

    # get the sequence data
    url = f"https://rest.ensembl.org/sequence/id/{ensembl_gene_id}"
    params = {"content-type": "application/json", "type": "genomic"}
    data = _request(url, params, verbose)

    if verbose:
        with open(os.path.join(output_dir, "ensembl_gene.json"), "w") as f:
            json.dump(data, f, indent=4)

    # translate the longest open reading frame to an AA sequence
    # TODO - find out if we care about introns here or not
    orf = Bio.Seq.Seq(_get_longest_orf_aa(data['seq']))
    aa = orf.translate()
    LOGGER.debug(aa)

    # write the fasta
    with open(fasta_file, "w") as f:
        f.write(f">{data['desc']}\n")
        f.write(f"{data['seq']}\n")
        f.write(f">{'AA'}\n")
        f.write(f"{str(aa)}\n")


def get_homologs(ensembl_gene_id: str, homolog_file: str,  output_dir:str, verbose: bool=False) -> None:
    """Get list of species which are homologous to a specified gene

    Args:
        ensembl_gene_id (str): Ensembl Gene ID
        homolog_file (str): output file
        output_dir (str): output directory (only used with verbose)
        verbose (bool, optional): More verbose output.   Defaults to False.
    """
    url = f"https://rest.ensembl.org/homology/id/{ensembl_gene_id}"
    params = {"content-type": "application/json", "layout": "condensed", "sequence": "none"}
    data = _request(url, params, verbose)

    if verbose:
        with open(os.path.join(output_dir, "ensembl_homolog.json"), "w") as f:
            json.dump(data, f, indent=4)

    # identify all the unique species specified - sort & write out
    species = set()
    if data.get("data") and len(data["data"]) > 0:
        for homology in data["data"][0].get("homologies", {}):
            species.add(homology["target"]["species"])
    else:
        LOGGER.warning("No homology data for {ensembl_gene_id}")
    species.remove("homo_sapiens") #TODO - include or not include?   Human-specific?

    species = list(species)
    species.sort()

    with open(homolog_file, "w") as f:
        for s in species:
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
    LOGGER.setLevel(logging.DEBUG) # base level

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


def _request(url: str, params:dict=None, verbose:bool=False) -> dict:
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


def _get_longest_orf_aa(dna:str) -> str:
    """Get longest open reading frame in a DNA strand

    Args:
        dna (str): DNA transcript

    Returns:
        str: AA of longest open reading frame.  None if not found.
    """
    regex = re.compile(r'ATG(?:[ACTG]{3})*?(?:TAA|TAG|TGA)')
    hits = regex.findall(dna)
    if hits:
        longest = max(hits, key = len)
        LOGGER.debug(len(longest))
        LOGGER.debug(longest)
    else:
        longest = None

    return longest
    

def main():
    """main"""
    #TODO - figure out if including species is a bad idea (just support human)
    args = parse_arguments()
    LOGGER.info("-- Setup output --")
    output = setup_outputs(args.gene_name, args.output_dir, args.force)

    LOGGER.info("-- get ensembl ID from mygene.info --")
    ensembl_gene_id = get_ensembl_gene_id(args.gene_name, args.species, args.output_dir, args.verbose)
    LOGGER.info(f"Ensembl ID: {ensembl_gene_id}")

    LOGGER.info("-- get nucleotide sequence via Ensembl --")
    LOGGER.info("-- translate longest open reading frame to AA --")
    LOGGER.info("-- write to fasta --")
    get_fasta(ensembl_gene_id, output.fasta_file, args.output_dir, args.verbose)

    LOGGER.info("-- get homologous genes via Ensembl --")
    get_homologs(ensembl_gene_id, output.homolog_file, args.output_dir, args.verbose)
    LOGGER.info("-- END ANALYSIS --")

if __name__ == "__main__":
    main()