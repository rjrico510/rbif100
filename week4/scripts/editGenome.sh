#!/bin/bash -xe
#
# Script which takes a folder of fastas and inserts a base preceeding NGG in a CRISPR site;
# For each fasta
# - finds all NGG with >= 20 bases upstream
# - outputs a new fasta where NGG -> <base>NGG
#
# Assumptions:
# - fasta file inputs are named <exome>_*.fasta
#
# input:
# - fasta dir 
# - output dir (defaults to input dir)
#
# output:
# - fastas in output dir named <exome>_postcrispr.fasta
#

FASTA_DIR=$1
BASE=${2:-"A"}
OUTPUT_DIR=${3:-$1}

# report inputs
echo "inputs:"
echo "fasta dir: ${FASTA_DIR}"
echo "base: ${BASE}"
echo "output dir: ${OUTPUT_DIR}"

mkdir -p "${OUTPUT_DIR}"

for FASTA_FILE in "$FASTA_DIR"/*.fasta; do
    # setup
    # TODO - revisit - does this make sense if everything is in the same dir?
    EXOME=$(basename "${FASTA_FILE}" | sed -r -e "s/([a-zA-Z]+)_.*.fasta/\1/")
    OUT_FILE="${OUTPUT_DIR}/${EXOME}_postcrispr.fasta"

    # search for 20 bases + NGG
    echo "modifying ${FASTA_FILE} ..."
    sed -r "s/([ATCG]{20})([ATCG]GG)/\1${BASE}\2/g" "${FASTA_FILE}" > "${OUT_FILE}"
done
