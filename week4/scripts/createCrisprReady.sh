#!/bin/bash -xe
#
# Script which takes a folder of exomes and a list of motifs,
# and for each exome creates a fasta of only the sequences containing 
# the top 3 motifs
#
# input:
# - motif file (list of sequences, 1 per row; no header)
# - exome dir 
# - output dir
#
MOTIFS_FILE=$1
EXOME_DIR=$2
OUTPUT_DIR=${3:-$2}

DEBUG=1 # debugging

# report inputs
echo "inputs:"
echo "motif file: ${MOTIFS_FILE}"
echo "exome dir: ${EXOME_DIR}"
echo "output dir: ${OUTPUT_DIR}"

mkdir -p "${OUTPUT_DIR}"

for FASTA_FILE in "$EXOME_DIR"/*.fasta; do
    # setup
    EXOME=$(basename "${FASTA_FILE}" | sed "s/.fasta//g")
    OUT_FILE="${OUTPUT_DIR}/${EXOME}_topmotifs.fasta"
    MOTIFS_COUNT="${OUTPUT_DIR}/${EXOME}_motif_count.txt"

    # get the count of each motif and output to a file
    while read -r MOTIF; do
        echo "${MOTIF}" "$(grep -o "${MOTIF}" "${FASTA_FILE}" | wc -l)" >> "${MOTIFS_COUNT}"
    done <"${MOTIFS_FILE}"

    # https://www.unix.com/shell-programming-and-scripting/178162-converting-column-row.html
    # https://stackoverflow.com/questions/39420589/how-to-handle-bash-sort-of-for-tie-conditions
    # 
    # sort the motif file, get the top 3, and turn the motifs into a string usable by grep
    PATTERN=$(sort -k 2rn "${MOTIFS_COUNT}" | head -3 | cut -d' ' -f1 | awk 'BEGIN { ORS="|" } {print}')
    PATTERN=${PATTERN%?} # remove trailing "|"

    # write the fastas matching any motif to output
    grep -E -B 1 --no-group-separator "${PATTERN}" "${FASTA_FILE}" > "${OUT_FILE}"

    # cleanup
    if [ "${DEBUG}" -ne 1 ]; then
        rm -f "${MOTIFS_COUNT}"
    fi
done