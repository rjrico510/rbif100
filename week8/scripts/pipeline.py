#!/usr/bin/env python3

import Bio.Seq
import json
import os
import re
import requests

def get_ensembl_gene_id(name: str, species: str) -> str:
    """Get ensembl ID from mygene.info

    Args:
        name (str): gene name
        species (str): species

    Returns:
        str: Ensembl ID (None if not found)
    """

    url = "https://mygene.info/v3/query"
    params = {
        "q": name,
        "species": [species],
        "fields": "all"
    }
    data = _request(url, params)

    # debug
    with open("mygene.json", "w") as f:
        json.dump(data, f, indent=4)

    try: #TODO clean this up - check if list has entries rather than just 0
        ensembl_gene_id = data["hits"][0]["ensembl"]["gene"]
    except KeyError:
        print(f"MyGeneInfo - no ensembl gene ID found")
        ensembl_gene_id = None
        
    return ensembl_gene_id


def get_sequence(ensembl_gene_id: str, fasta_file: str) -> None:
    """Get gene sequence
       Get longest open reading frame in the sequence and convert to an AA sequence
       Write both to a fasta file

    Args:
        ensembl_gene_id (str): Ensembl gene ID
        fasta_file (str): fasta file to write to
    """

    # get the sequence data
    url = f"https://rest.ensembl.org/sequence/id/{ensembl_gene_id}"
    params = {"content-type": "application/json", "type": "genomic"}
    data = _request(url, params)
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


def get_homologs(ensembl_gene_id, homolog_file):
    #url = f"https://www.ncbi.nlm.nih.gov/homologene/?term=Homo+sapiens+MC1R"
    url = f"https://rest.ensembl.org/homology/id/{ensembl_gene_id}"
    params = {"content-type": "application/json", "layout": "condensed"}
    data = _request(url, params)

    # debug
    with open("ensembl_homolog.json", "w") as f:
        json.dump(data, f, indent=4)

    species = set()
    for homology in data["data"][0]["homologies"]:
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

def _request(url: str, params:dict=None) -> dict:
    """Executes a request

    Args:
        url (str): URL for the request
        params (dict, optional): Dictionary of query parameters. Defaults to None.

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
    """Get longest open reading frame in a cDNA strand

    Args:
        dna (str): DNA transcript

    Returns:
        str: AA of longest open reading frame
    """
    regex = re.compile(r'ATG(?:[ACTG]{3})*?(?:TAA|TAG|TGA)')
    hits = regex.findall(dna)
    if hits:
        print(len(hits))
        longest = max(hits, key = len)
        print(len(longest))
        print(longest)
    else:
        longest = None

    return longest
    

def main():
    # TODO - parameterize
    # TODO - check for file existence
    # TODO - set a debug flag
    gene_name = "MC1R"
    species = "human"
    fasta_file = "transcript.fasta"
    homolog_file_path = "."
    homolog_file_root = "_homology_list.txt"
    homolog_file = os.path.join(homolog_file_path, f"{gene_name}{homolog_file_root}")

    # get ensembl ID from mygene.info
    ensembl_gene_id = get_ensembl_gene_id(gene_name, species)
    print(ensembl_gene_id)
    # get transcript sequence from ensembl
    # translate longest open reading frame to AA
    # write to fasta
    get_sequence(ensembl_gene_id, fasta_file)
    # get homologous genes
    get_homologs(ensembl_gene_id, homolog_file)


if __name__ == "__main__":
    main()