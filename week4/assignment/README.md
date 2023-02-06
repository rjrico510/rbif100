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
  - Create a new fasta (exome_topmotifs.fasta) with only the sequences matching any of the top three motifs
- identifyCrisprSite.sh: for each fasta created in the previous step:
  - Find all instances of NGG with at least 20 bases upstream
  - Create a new fasta (exome_precrispr.fasta) with only the sequences with matching sites
- editGenome.sh: for each fasta created in the previous step:
  - Insert a base (A) before the NGG in the positions identified in the previous step
  - Create a new fasta (exome_postcrispr.fasta) with the new sequences
- exomeReport.py: generate a report containing:
  - summary information for each exome that passed the initial filtering criteria
  - a count and list of the union of all genes identified as having crispr sites

## Usage

`./copyExomes.sh <clinical data file> <exome directory> <output directory>`

`./createCrisprReady.sh <motif file> <input directory> <output directory (optional)>`

`./identifyCrisprSite.sh <input directory> <output directory (optional)>`

`./editGenome.sh <input directory> <output directory (optional)>`

`python3 exomeReport.py <clinical data file> <input directory>`

- The intermediate scripts take optional output directories.  If not specified, they write to the input folder.
- For additional details see the documentation of each individual script.

## Assignment Commands

The following commands will run the assignment:

`./copyExomes.sh clinical_data.txt exomes exomesCohort`

`./createCrisprReady.sh motif_list.txt exomesCohort CrisprReady`

`./identifyCrisprSite.sh CrisprReady PreCrispr`

`./editGenome.sh PreCrispr PostCrispr`

`python3 exomeReport.py clinical_data.txt PostCrispr`

## Assumptions

- The clinical data file matches the format and header of the example data
- The motifs file is one line per motif
- All fastas and motifs are uppercase
- All sequences in fasta files are on a single line
- There is no special handling of cases where an NGG falls inside the 20-base upstream region
  - i.e. there is no affordances made for overlapping search hits
  - the code will search left to right, insert the new base at the first hit, and resume from the end of the hit. e.g.
    - ACCTTCTTACAACATTATAACAGAGGGTTTACACCTCATGG becomes
    - ACCTTCTTACAACATTATAACAGAAGGGTTTACACCTCATGG

## Contents

- README.md - this file
- clinical_data.txt - input: clinical data file
- motif_list.txt - input: list of motifs
- exomes - input: directory of exomes
- copyExomes.sh - copies exomes matching criteria from a clinical data file
- createCrisprReady.sh - creates fastas matching top 3 motifs for each exome passing the clinical data criteria
- identifyCrisprSite.sh - creates fastas for each exome that have a matching site
- editGenome.sh - creates fastas with an inserted A in front of NGG
- exomeReport.py - creates summary report
- exomesCohort - output of copyExomes.sh
- CripsrReady - output of createCrisprReady.sh
- PreCrispr - output of identifyCrisprSite.sh
- PostCrispr - output of editGenome.sh
- exomeReport.txt - output of exomeReport.py
- run.sh - script used to run the data

## Development Notes

- createCrisprReady.sh has a VERY long line of bash which creates a search pattern for motifs in a single line.
  - The implementation generates an intermediate file for debugging, which it disposes of at the end (unless debugging is on).
  - The original implementation was a much simpler one which wrote the motif count to an intermediate file, then created a search string by reading the file back in.
  - I went back and forth on which implementation was "better" - in practice I might be more likely to use the original one in production.    However, I ended up using the one-liner since it was a useful exercise in bash.
  - I kept the simpler one around: https://github.com/rjrico510/rbif100/blob/main/week4/scripts/createCrisprReady_ORIGINAL.sh
- The positional arguments in editGenome.sh include an optional base (or sequence) to insert which defaults to A.
  - This should probably be replaced with a shift/case construct
- The scripts specifically look for fastas named by their preceding scripts, e.g. identifyCrisprSite.sh specifically looks for files matching "*_topmotifs.fasta".
  - This allows all the data to be written to the same directory if desired.
  - This helps ensure each script only reads in fastas which are relevant.
