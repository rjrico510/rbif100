#!/usr/bin/env python3
"""TODO - top-level docstring

"""

import argparse
import Bio.Seq
import json
import os
import re
import requests
import sys
import typing


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

    parser = argparse.ArgumentParser(description="Given a human gene name, get the sequence, AA of longest open reading frame, and homologs")
    parser.add_argument("gene_name", help="gene name")
    parser.add_argument("-s", "--species", default=DEFAULT_SPECIES, help="species (defau;t human)")
    parser.add_argument("-o", "--output-dir", dest="output_dir", default=DEFAULT_OUTPUT_DIR, help="output folder (default current location)")
    parser.add_argument("-f", "--force", action="store_true",  help="force overwrite of existing output")
    parser.add_argument("-v", "--verbose", action="store_true", help="verbose - more logging and outputs")
    args = parser.parse_args()

    # echo inputs
    print(f"Gene name: {args.gene_name}")
    print(f"Species: {args.species}")
    print(f"Output directory: {args.output_dir}")
    print(f"Force overwrite: {args.force}")
    print(f"Verbose: {args.verbose}")

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
    FASTA_FILENAME_ROOT = "_transcript.fasta"
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
                    print(f"{output_file} exists - will overwrite")
                else:
                    print(f"{output_file} already exists - exiting...")
                    sys.exit(1)

    return output_files

def get_ensembl_gene_id(name: str, species: str, verbose: bool=False) -> str:
    """Get ensembl ID from mygene.info

    Args:
        name (str): gene name
        species (str): species
        verbose (bool, optional): More verbose output.   Defaults to False.

    Returns:
        str: Ensembl ID (None if not found)
    """

    url = "https://mygene.info/v3/query"
    params = {
        "q": name,
        "species": [species],
        "fields": "symbol,name,ensembl,taxid"
    }
    data = _request(url, params, verbose)

    # debug
    with open("mygene.json", "w") as f:
        json.dump(data, f, indent=4)

    try: #TODO clean this up - check if list has entries rather than just 0
        ensembl_gene_id = data["hits"][0]["ensembl"]["gene"]
    except KeyError:
        print(f"MyGeneInfo - no ensembl gene ID found")
        ensembl_gene_id = None
        
    return ensembl_gene_id


def get_fasta(ensembl_gene_id: str, fasta_file: str, verbose: bool=False) -> None:
    """Get gene sequence
       Get longest open reading frame in the sequence and convert to an AA sequence
       Write both to a fasta file

    Args:
        ensembl_gene_id (str): Ensembl gene ID
        fasta_file (str): fasta file to write to
        verbose (bool, optional): More verbose output.   Defaults to False.
    """

    # get the sequence data
    url = f"https://rest.ensembl.org/sequence/id/{ensembl_gene_id}"
    params = {"content-type": "application/json", "type": "genomic"}
    data = _request(url, params, verbose)
    # TODO - check what really is needed here - I'm getting the entire genomic sequence

    # debug
    with open("ensembl.json", "w") as f:
        json.dump(data, f, indent=4)

    # translate the longest open reading frame to an AA sequence
    # TODO - find out if we care about introns here or not
    orf = Bio.Seq.Seq(_get_longest_orf_aa(data['seq']))
    aa = orf.translate()
    print(aa)

    # write the fasta
    with open(fasta_file, "a") as f:
        f.write(f">{data['desc']}\n")
        f.write(f"{data['seq']}\n")
        f.write(f">{'AA'}\n")
        f.write(f"{str(aa)}\n")


def get_homologs(ensembl_gene_id: str, homolog_file: str, verbose: bool=False) -> None:
    """Get list of species which are homologous to a specified gene

    Args:
        ensembl_gene_id (str): Ensembl Gene ID
        homolog_file (str): output file
        verbose (bool, optional): More verbose output.   Defaults to False.
    """
    url = f"https://rest.ensembl.org/homology/id/{ensembl_gene_id}"
    params = {"content-type": "application/json", "layout": "condensed", "sequence": "none"}
    data = _request(url, params, verbose)

    # debug
    with open("ensembl_homolog.json", "w") as f:
        json.dump(data, f, indent=4)

    # identify all the unique species specified - sort & write out
    species = set()
    for homology in data["data"][0]["homologies"]: # TODO - check if entry is present
        species.add(homology["target"]["species"])
    species.remove("homo_sapiens") #TODO - include or not include?

    species = list(species)
    species.sort()

    with open(homolog_file, "w") as f:
        for s in species:
            f.write(f"{s}\n")

#
# helpers
#

def _request(url: str, params:dict=None, verbose:bool=False) -> dict:
    """Executes a request

    Args:
        url (str): URL for the request
        params (dict, optional): Dictionary of query parameters. Defaults to None.
        verbose (bool, optional): More verbose output.   Defaults to False.

    Returns:
        dict: json output of the response
    """
    response = requests.get(url, params=params)
    if response.status_code != 200: #TODO - better handle this
        print(f"API call failure: {url} - response code {response.status_code}")
        data = None
    else:
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
        print(len(longest))
        print(longest)
    else:
        longest = None

    return longest
    

def main():
    """main
    """
    # setup inputs/outputs
    args = parse_arguments()
    output = setup_outputs(args.gene_name, args.output_dir, args.force)

    # get ensembl ID from mygene.info
    ensembl_gene_id = get_ensembl_gene_id(args.gene_name, args.species, args.verbose)
    print(ensembl_gene_id)

    # get nucleotide sequence via Ensembl
    # translate longest open reading frame to AA
    # write to fasta
    get_fasta(ensembl_gene_id, output.fasta_file, args.verbose)

    # get homologous genes via Ensembl
    get_homologs(ensembl_gene_id, output.homolog_file, args.verbose)


if __name__ == "__main__":
    main()