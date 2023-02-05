#!/bin/bash -xe
#
# Script which takes samples with a given diameter range (inclusive) & have been sequenced
# and copies their exome from a given folder to a new directory.
#
# input:
# - clinical file (see below)
# - folder of exome fastas
# optional inputs: (must be included in order if present)
# - output folder (optional: default: exomesCohort)
# - lower bound (optional: default 20) 
# - upper bound (optional: default 30)
# output:
# - folder of fastas meeting the above criteria
#
# Clinical data file format:
# - tab-delimited
# - header:
# Discoverer	Location	Diamater (mm)	Environment	Status	code_name
# (string)      (string)    (int)           (string)    (string)(string)
# - Status is either "Sequenced" or "not sequenced" - former string is a match
# - code_name must match a fasta in the exome folder, e.g.there must be a code_name.fasta
#
# usage: ./copyExomes.sh <CLINCAL FILE> <EXOME DIR> <OUTPUT DIR (optional)> <LOWER BOUND (optional)> <UPPER BOUND (optional)>

CLINICAL_FILE=$1
EXOME_DIR=$2
OUTPUT_DIR=${3:-exomesCohort}
LOWER=${4:-20}
UPPER=${5:-30}

# report inputs
echo "inputs:"
echo "clinical file: ${CLINICAL_FILE}"
echo "exome dir: ${EXOME_DIR}"
echo "output dir: ${OUTPUT_DIR}"
echo "lower bound: ${LOWER}"
echo "upper bound: ${UPPER}"

# create the output dir
if [ -d "${OUTPUT_DIR}" ]; then
    echo "${OUTPUT_DIR} already exists - exiting"
    exit 2
else
    mkdir -p "${OUTPUT_DIR}"
fi

# for each row in the clinical file:
# - extract the diameter, status and code name
# - keep only the records within the diameter range and which have been sequenced
# - extract the remaining code names and copy the exomes to the output directory
cut -f3,5,6 "${CLINICAL_FILE}" | awk -v lo="${LOWER}" -v up="${UPPER}" '$1 >= lo && $1 <= up && $2 == "Sequenced"' | cut -f3 | xargs -n 1 -I {} cp "${EXOME_DIR}"/{}.fasta "${OUTPUT_DIR}"/{}.fasta
