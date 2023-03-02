#!/usr/bin/env python3

import Bio.Seq
import json
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

    try: # hack - check if list has entries rather than just 0
        ensembl_gene_id = data["hits"][0]["ensembl"]["gene"]
    except KeyError:
        print(f"MyGeneInfo - no ensembl gene ID found")
        ensembl_gene_id = None
        
    return ensembl_gene_id


def get_sequence(ensembl_gene_id: str, fasta_file: str):

    url = f"https://rest.ensembl.org/sequence/id/{ensembl_gene_id}"
    params = {"content-type": "application/json"}
    data = _request(url, params)
    # TODO - check what really is needed here - I think I'm getting introns + exons (DNA vs cDNA)

    # debug
    with open("ensembl.json", "w") as f:
        json.dump(data, f, indent=4)

    with open(fasta_file, "w") as f:
        f.write(f">{data['desc']}\n")
        f.write(f"{data['seq']}\n")

    # WIP
    orf = Bio.Seq.Seq(_get_longest_orf_aa(data['seq']))
    aa = orf.translate()
    print(aa)


# def get_homologs(species, gene_name):
#     url = f"https://www.ncbi.nlm.nih.gov/homologene/?term=Homo+sapiens+MC1R"
#     data = _request(url)
#     print(data)
    


def _request(url, params=None):
    #TODO - better handle case of URL issue
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"API call failure: {url} - response code {response.status_code}")
        data = None
    else:
        data = response.json()
    return data


def _get_longest_orf_aa(dna:str) -> str:
    """_summary_

    Args:
        dna (str): DNA transcript

    Returns:
        str: AA of longest open reading frame
    """
    regex = re.compile(r'ATG(?:[ACTG]{3})*?(?:TAA|TAG|TGA)')
    hits = regex.search(dna)
    if hits:
        print(hits.groups())
    else:
        print("No hits")
    return None
    
    


def main():
    # TODO - parameterize
    gene_name = "MC1R"
    species = "human"
    fasta_file = "transcript.fasta" 

    # get ensembl ID from mygene.info
    ensembl_gene_id = get_ensembl_gene_id(gene_name, species)
    print(ensembl_gene_id)
    # get transcript sequence from ensembl
    # translate longest open reading frame to AA (stop codons are TAG/TAA/TGA)
    get_sequence(ensembl_gene_id, fasta_file)
    # get homologous genes (?)
    #get_homologs(species, gene_name)


if __name__ == "__main__":
    main()