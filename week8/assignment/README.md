# RBIF100 Assignment 1 (Week 8)

 Author: Rudy Rico

 email: rrico@brandeis.edu

 github: https://github.com/rjrico510/rbif100/tree/main/week8

## Goals

Given the following inputs:

- a gene name
- a species (currently only homo sapiens is supported)
- a sample file containing name, color, and barcode for each sample

Create a script `pipeline.py` which performs the following:

- Calls the mygene.info API to get the Ensembl ID for the gene
- Uses the Ensembl ID to get the gene sequence from the Ensembl API
- Identifies the longest open reading frame and converts it to an amino acid sequence
- Writes the gene DNA sequence and longest reading frame AA sequence to a fasta file
- Identifies all other species with homologous genes and writes them to a text file (sorted list, 1 column)

## Usage

`python3 pipeline.py <gene>`

- There are additional optional flags to control
  - species (currently only homo sapiens is supported)
  - the output directory
  - whether or not to overwrite existing data
  - whether or not to report additional debugging information
  - log file name
- For additional details: `python3 pipeline.py -h`

- The code will exit if
  - any input is not found
  - the outputs exist and `--force` is not specified
  - any API call fails


## Assignment Commands

The following commands will run the assignment:

`python3 pipeline.py MC1R`

## Assumptions

- The gene name is a common name
- The longest open reading frame in the gene DNA sequence is not necessarily biologically meaningful

## Contents

- README.md - this file
- pipeline.py - the python script which runs the analysis
- MC1R_gene_AA.fasta - gene sequence and amino acid sequence fasta
- MC1R_homology_list.txt - sorted list of species with homologous genes
- pipeline.log - output: log file
- run.sh - script used to run the data

## Development Notes

- There is a skeleton for possibly handling more than one species.
  - The SPECIES map is intended as an initial pass at handling this
  - This only deals with human, but at least pulls anything species-specific out of the code.
- There are unit tests for the open reading frame method:
https://github.com/rjrico510/rbif100/tree/main/week8/scripts/test_pipeline.py
- The code was also tested on
  - TDF: https://github.com/rjrico510/rbif100/tree/main/week8/analysis/assignment/baseline
