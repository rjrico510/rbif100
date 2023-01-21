#!/bin/bash
#
# Script which counts the number of occurrences of 1+ motifs in a fastq
# and produces a folder of fasta files, each of which is named after
# the motif and includes only sequences containing the motif
#
# input:
# - fasta file
# - text file containing a list of motifs (1 per line)
# output:
# - folder of fastas (default name: motifs)
#
# usage: ./motif_counter.sh <FASTA FILE> <MOTIFS FILE> <MOTIFS OUTPUT FOLDER (optional)> <MOTIFS COUNT FILE (optional)

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

# exit if output already exists; otherwise create output folder
if [ -f "${MOTIFS_COUNT}" ]; then
  echo "${MOTIFS_COUNT} already exists - exiting"
  exit 2
elif [ -d "${MOTIFS_FOLDER}" ]; then
  echo "${MOTIFS_FOLDER} already exists - exiting"
  exit 2
else
  mkdir -p "${MOTIFS_FOLDER}"
fi

# for each motif in the motif file:
# (1) search for all matches (including the preceeding description line), omitting the delimiter
# (2) append the motif & # occurrences to the count file

while read -r MOTIF; do
  echo "searching for ${MOTIF} in ${FASTA_FILE} ..."
  grep -B 1 --no-group-separator "${MOTIF}" "${FASTA_FILE}" > "${MOTIFS_FOLDER}/${MOTIF}.fasta"
  echo "${MOTIF}" "$(grep -o "${MOTIF}" "${MOTIFS_FOLDER}/${MOTIF}.fasta" | wc -l)" >> "${MOTIFS_COUNT}"
done <"${MOTIFS_FILE}"