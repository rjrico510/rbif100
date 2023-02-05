# RBIF100 Assignment 1 (Week 4)

 Author: Rudy Rico

 email: rrico@brandeis.edu

 github: https://github.com/rjrico510/rbif100/tree/main/week4

## Goals:

Given the following inputs:

- a clinical data file
- a list of motifs
- a directory of exome fastas

Create the following scripts:

- copyExomes.sh:
  - Identify exomes corresponding to sequenced samples of diameter 20-30 mm (inclusive)
  - Copy exomes to a new directory exomesCohort
- createCrisprReady.sh: for each exome in exomesCohort:
  - Identify the top three motifs present
  - Create a new fasta with only the sequences matching any of the top three motifs
- identifyCrisprSite.sh: for each fasta created in the previous step:
  - Find all instances of NGG with at least 20 bases upstream
  - Create a new fasta with only the sequences with matching sites
- editGenome.sh: for each fasta created in the previous step:
  - Insert a base (A) before the NGG in the positions identified in the previous step
  - Create a new fasta with the new sequences
- exomeReport.py: generate a report containing:
  - summary information for each exome that passed the initial filtering criteria
  - a count and list of the union of all genes identified as having crispr sites

## Usage
 `./week2.sh fasta_file motifs_file`


## Assignment Commands


## Assumptions

- foo

## Contents

- foo
