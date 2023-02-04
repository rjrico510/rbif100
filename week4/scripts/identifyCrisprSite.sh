#!/bin/bash -xe
#
# Script which takes a folder of fastas and identifies a suitable CRISPR site;
# For each fasta
# - finds all NGG with >= 20 bases upstream
# - outputs a new fasta of only the matching entries
#
# Assumptions:
# - fasta file inputs are named <exome>_*.fasta
#
# input:
# - fasta dir 
# - output dir (defaults to input dir)
#
# output:
# - fastas in output dir named <exome>_precrispr.fasta
#

FASTA_DIR=$1
OUTPUT_DIR=${2:-$1}

mkdir -p "${OUTPUT_DIR}"

for FASTA_FILE in "$FASTA_DIR"/*.fasta; do
    # setup
    # TODO - revisit - does this make sense if everything is in the same dir?
    EXOME=$(basename "${FASTA_FILE}" | sed -r -e "s/([a-zA-Z]+)_.*.fasta/\1/")
    OUT_FILE="${OUTPUT_DIR}/${EXOME}_precrispr.fasta"

    # search for 20 bases + NGG
    echo "searching ${FASTA_FILE} ..."
    grep -E "[ATCG]{21}GG" -B 1 --no-group-separator "${FASTA_FILE}" > "${OUT_FILE}"
done
