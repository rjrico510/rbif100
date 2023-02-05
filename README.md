# RBIF100 Assignment 1 (Week 4)

 Author: Rudy Rico

 email: rrico@brandeis.edu

 github: https://github.com/rjrico510/rbif100/tree/main/week4

## Goals

 Given the following inputs:

- clinical data file
- list of motifs
- folder of exome fastas

Create the following scripts:

- copyExomes.sh: copy exomes wtih diameter between 20-30 mm (inclusive) that have been sequenced to folder exomesCohort
- createCriprReady.sh: For each fasta in the exomesCohort
  - identify the top three motifs
  - create an exome_topmotifs.fasta contaning only the sequences containing any of the top three motifs
- identifyCrisprSite.sh: For each fasta created by createCriprReady.sh:
  - identify all sequences with NGG and which contain 20+ bases upstream
  - create an exome_preCrispr.fasta file containing only the matching sequences
- editGenome.sh: for each fasta created by identifyCrisprSite.sh:
  - for thr match sequences from the previous script, insert an A in front of NGG
  - create an exome_posyCrispr.fasta file containing the modified sequences
- exomeReport.py: produce a report of all exomes in the cohort and the common genes

## Usage

 `./copyExomes.sh clinical_data.txt exomes_directory <output directory>`

 `./createCrisprReady.sh motif_list.txt <input directory> <output directory>`

 `./identifyCrisprSite.sh <input directory> <output directory>`

 `./editGenome.sh <input directory> <output directory>`

 `python3 exomeReport.py clinical_data.txt <postCrispr directory>`

## Script Notes

- See the individual script documentation for further details
- Each script can take an optional output directory; if omitted the results are written to the input directory
- The scripts will exit if a file they need to write already exists

## Assignment Commands

To run the assignment:

 `./copyExomes.sh clinical_data.txt exomes exomesCohort`

 `./createCrisprReady.sh motif_list.txt exomesCohort CrisprReady`

 `./identifyCrisprSite.sh CrisprReady PreCrispr`

 `./editGenome.sh PreCrispr PostCrispr`

 `python3 exomeReport.py clinical_data.txt PostCrispr`

## Assumptions

- The clinical file is always of the format specified by the class example (headers/columns)
- The motifs file is a text file with exactly 1 motif per line
- The fasta file does not split the sequence portion via line feeds, i.e. the entire sequence is on one line.

## Contents of the week4 folder

- README.md (this file)
- copyExomes.sh - copies the exomes matching the clinical data criteria
- createCrisprReady.sh - creates fastas of top motifs
- identifyCrisprSite.sh - creates fastas of crispr sites
- editGenome.sh - creates fastas of crispr-modified sites
- exomeReport.py - python 3 file to generate report
- motif_list.txt - input list of motifs
- clinical_data.txt - input clinical data
- exomes - input fasta directory
- run.sh - the actual command use to run the data to get to this output
- exomesCohort - output of copyExomes.sh
- CripsrReady - output of createCrisprReady.sh
- PreCrispr - output of identifyCrisprSite.sh
- PostCrispr - output of editGenome.sh
- exomeReport.txt - output of exomeReport.py

## Notes

The linked git repository includes:

- all of the above
- a python implementation to verify the result

## Development Notes

- The bash script was written using vscode & linted with the ShellCheck extension.
- The base option in editGenome.sh would be better implemented via flags (shift/case)
