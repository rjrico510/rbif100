#!/bin/bash -xe
#
# Script which takes a folder of fastas and identifies a suitable CRISPR site;
# For each fasta
# - finds all NGG with >= 20 bases upstream
# - outputs a new fasta of only the matching entries
#
# Assumptions:
# - fasta file inputs are named <exome>_topmotifs.fasta
#
# input:
# - fasta dir of files named <exome>_topmotifs.fasta
# - output dir (defaults to input dir)
#
# output:
# - fastas in output dir named <exome>_precrispr.fasta
#
# usage: ./identifyCrisprSite.sh <FASTA DIR> <OUTPUT_DIR (optional)>

FASTA_DIR=$1
OUTPUT_DIR=${2:-$1}

# report inputs
echo "inputs:"
echo "fasta dir: ${FASTA_DIR}"
echo "output dir: ${OUTPUT_DIR}"

mkdir -p "${OUTPUT_DIR}"

for FASTA_FILE in "$FASTA_DIR"/*_topmotifs.fasta; do
    # setup
    EXOME=$(basename "${FASTA_FILE}" | sed -r -e "s/([a-zA-Z]+)_.*.fasta/\1/")
    OUT_FILE="${OUTPUT_DIR}/${EXOME}_precrispr.fasta"

    # don't overwrite - exit if output exists
    if [ -f "${OUT_FILE}" ]; then
        echo "${OUT_FILE} already exists - exiting"
        exit 2
    fi

    # search for 20 bases + NGG
    # TODO - what if GG is contained in the 1st 20 bases?
    echo "searching ${FASTA_FILE} ..."
    grep -E "[ATCG]{21}GG" -B 1 --no-group-separator "${FASTA_FILE}" > "${OUT_FILE}"
done
