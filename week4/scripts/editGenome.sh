#!/bin/bash -xe
#
# Script which takes a folder of fastas and inserts a base preceeding NGG in a CRISPR site;
# For each fasta
# - finds all NGG with >= 20 bases upstream
# - outputs a new fasta where NGG -> <base>NGG
#
# Assumptions:
# - fasta file inputs are named <exome>_precrispr.fasta
#
# input:
# - fasta dir 
# - output dir (defaults to input dir)
# - base (or sequence to insert) (defaults to A) (must specify output dir as well if this is specified)
#
# output:
# - fastas in output dir named <exome>_postcrispr.fasta
#
# usage: ./editGenome.sh <FASTA DIR> <OUTPUT DIR (optional)> <BASE (optional)>

FASTA_DIR=$1
OUTPUT_DIR=${2:-$1}
BASE=${3:-"A"}

# report inputs
echo "inputs:"
echo "fasta dir: ${FASTA_DIR}"
echo "output dir: ${OUTPUT_DIR}"
echo "base: ${BASE}"

mkdir -p "${OUTPUT_DIR}"

for FASTA_FILE in "$FASTA_DIR"/*_precrispr.fasta; do
    # setup
    EXOME=$(basename "${FASTA_FILE}" | sed -r -e "s/([a-zA-Z]+)_.*.fasta/\1/")
    OUT_FILE="${OUTPUT_DIR}/${EXOME}_postcrispr.fasta"

    # don't overwrite - exit if output exists
    if [ -f "${OUT_FILE}" ]; then
        echo "${OUT_FILE} already exists - exiting"
        exit 2
    fi

    # search for 20 bases + NGG
    echo "modifying ${FASTA_FILE} ..."
    sed -r "s/([ATCG]{20})([ATCG]GG)/\1${BASE}\2/g" "${FASTA_FILE}" > "${OUT_FILE}"
done
