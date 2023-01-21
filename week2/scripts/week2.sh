#!/bin/bash
# usage: ./week2.sh <FASTA FILE> <MOTIFS FILE> <MOTIFS OUTPUT FOLDER (optional)> <MOTIFS COUNT FILE (optional)
# TODO - proper usage statement

FASTA_FILE=$1
MOTIFS_FILE=$2
MOTIFS_FOLDER=${3:-motifs}
MOTIFS_COUNT=${4:-motif_count.txt}

# report back the inputs
echo "inputs:"
echo "fasta: ${FASTA_FILE}"
echo "motifs: ${MOTIFS_FILE}"
echo "motif folder: ${MOTIFS_FOLDER}"
echo "motif count: ${MOTIFS_COUNT}"
echo

mkdir -p "${MOTIFS_FOLDER}" # TODO - check for presence

# for each motif in the motif file:
# (1) search for all matches (including the preceeding description line), omitting the delimiter
# (2) append the motif & # occurrences to the count file

while read -r MOTIF; do
  echo "searching for ${MOTIF} in ${FASTA_FILE} ..."
  grep -B 1 --no-group-separator "${MOTIF}" "${FASTA_FILE}" > "${MOTIFS_FOLDER}/${MOTIF}.txt"
  echo "${MOTIF}" "$(grep -o "${MOTIF}" "${MOTIFS_FOLDER}/${MOTIF}.txt" | wc -l)" >> "${MOTIFS_COUNT}"
done <"${MOTIFS_FILE}"