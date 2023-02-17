# RBIF100 Assignment 1 (Week 6)

 Author: Rudy Rico

 email: rrico@brandeis.edu

 github: https://github.com/rjrico510/rbif100/tree/main/week6

## Goals

Given the following inputs:

- a fastq of barcoded sequencing data
- a reference fasta
- a sample file containing name, color, and barcode for each sample

Create a script `pipeline.py` which performs the following:

- demultiplexes the fastq by barcode, and trims the barcode and low-quality trailing bases
  - anything beyond and including two consecutive bases bases with quality value D and/or F are trimmed
  - the resultng fastqs are written to a new fastqs directory
- align the reads to the reference via bwa
  - the resulting sam files are written to a new bam directory
- convert the sam files to sorted bam files and delete the sam files
- generate pileups via pysam and identify any SNPs
- generate a report of:
  - the SNP that caused each mold color (1-based position)
  - the # sequences per sample and % matching the mutation

## Usage

`python3 pipeline.py <sequencing data fastq> <sample file> <reference fasta>`

- There are additional optional flags to control
  - the output fastq and bam folder paths
  - the report name
  - whether or not to overwrite existing data
  - whether or not to re-run bwa index
  - whether or not to save the SAM files
- For additional details: `python3 pipeline.py -h`

- The code will exit if
  - any input is not found
  - the outputs exist and `--force` is not specified
  - `bwa` or `samtools` is not in the path
  - `pysam` is not importable
  - the sample barcode lengths are not all the same

- additional notes
  - any reads not matching a barcode are skipped

## Assignment Commands

The following commands will run the assignment:

`python3 pipeline.py hawkins_pooled_sequences.fastq harrington_clinical_data.txt dgorgon_reference.fa`

## Assumptions

- The sample file is a tab-delimited file with headers Name, Color, Barcode
- The barcode is at the beginning of each fastq read
- The barcodes are all the same length
- The only variants of interest are SNPs
- There are no bases with quality values with scores worse than D or F
- `bwa`, `samtools` and `pysam` are present

## Contents

- README.md - this file
- pipeline.py - the python script which runs the analysis
- hawkins_pooled_sequences.fastq - input: the sequencing data
- harrington_clinical_data.txt - input: the sample file
- dgorgon_reference.fa - input: the reference
- dgorgon_reference.fa.[amb/ann/bwt/pac/sa] - intermediate: the reference index files
- fastqs - output: directory of the demultiplexed and trimmed fastqs
- bams - output: directory of the sorted bam files and their indices
- report.txt - output: the text report
- run.sh - script used to run the data

## Development Notes

- The reporting code does not assume a single variant per color - but the report output itself does.
  - or at least gives no indication of more than one variant is found for a given color
- The wildtype is taken from the reference; a better way might be to take it from the MD tag.
  - Reading the entire reference is OK in this case but not scalable.
- The code was tested on two small datasets:
  - https://github.com/rjrico510/rbif100/tree/main/week6/data/test (2 samples; 8 reads taken from the assignment data)
  - https://github.com/rjrico510/rbif100/tree/main/week6/data/tinytest (2 samples; 4 synthetic reads with variants at known locations)
- There is only a check for `bwa` and `samtools`; if pysam is absent the script will immediately fail with a ModuleNotFoundError
