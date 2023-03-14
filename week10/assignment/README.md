# RBIF100 Assignment 1 (Week 10)

 Author: Rudy Rico

 email: rrico@brandeis.edu

 github: https://github.com/rjrico510/rbif100/tree/main/week10

## Goals

Given the following inputs:

- a clinical data file
- a directory of diversity scores (one per code_name from the clinical data file)
- a directory of distance data (one per code_name from the clinical data file)

Create a script `pipeline.py` which performs the following:
- Generates the mean and standard deviation of the diversity scores per species, and add to an updated clinical data file (this will not overwrite the existing file)
- Identify the top N and lowest M average diversity samples (defaults to N=2, M=1) and generate a PDF scatter plot of the distance data for each
- Generate a k-means plot for each

## Usage

`python3 pipeline.py <gene>`

- There are additional optional flags to control
  - number of top diversity samples to plot (default 2)
  - number of lowest diversity samples to plot (default 1)
  - output directory
  - name of new clinical data file
  - whether or not to overwrite existing data
  - whether or not to report additional debugging information
  - log file name
- For additional details: `python3 pipeline.py -h`

- The code will exit if
  - any input is not found or is not a file/directory
  - the outputs exist and `--force` is not specified
  - the old clinical data file and new clinical data file are the same file
- The code will warn if there is no distance data for a sample, but will continue.


## Assignment Commands

The following commands will run the assignment:

`python3 pipeline.py clinical_data.txt diversityScores distanceFiles`

## Assumptions

- The clinical data file is a tab-delimited file with a column `code_name`
- The files in the diversity scores directory are single-column and named <code_name>.diversity.txt
- The files in the distance files directory are csvs and named <code_name>.distance.txt
- There is a distance and diversity file for each `code_name` entry in the clinical data file
- Every diversity score file has the same number of scores

## Contents

- README.md - this file
- pipeline.py - the python script which runs the analysis
- clinical_data.txt - input: clinical data file
- diversityScores - input: directory of diversity scores
- distanceFiles - input: directory of distance files
- clinical_data_with_diversity.txt - output: clinical data file with additional statistics
- buffalo/fox/lion.pdf - output: scatter plots of distance data
- pipeline.log - output: log file
- run.sh - script used to run the data

## Development Notes

- The data was tested on one tiny test dataset for debugging:
  - https://github.com/rjrico510/rbif100/tree/main/week10/data/tinytest
- The creation date was removed from the PDF metadata to make PDF creation deterministic
  - The code was being tested by comparing checksums with a baseline; this wouldn't work otherwise 
