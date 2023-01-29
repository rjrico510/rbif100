#!/bin/bash
MOTIFS_FILE=motif_list.txt
EXOME_FOLDER=exomesCohort
OUTPUT_FOLDER=crisprReady
MOTIFS_COUNT=motif_count.txt

for FASTA_FILE in "$EXOME_FOLDER"/*.fasta; do
    while read -r MOTIF; do
        echo "${MOTIF}" "$(grep -o "${MOTIF}" "${FASTA_FILE}" | wc -l)" >> "${MOTIFS_COUNT}"
    done <"${MOTIFS_FILE}"
    # https://www.unix.com/shell-programming-and-scripting/178162-converting-column-row.html
    # https://stackoverflow.com/questions/39420589/how-to-handle-bash-sort-of-for-tie-conditions
    PATTERN=$(sort -k 2rn "${MOTIFS_COUNT}" | head -3 | cut -d' ' -f1 | awk 'BEGIN { ORS="|" } {print}')
    PATTERN=${PATTERN%?} # remove trailing "|"

    EXOME=$(basename "${FASTA_FILE}" | sed "s/.fasta//g")
    OUTFILE="${OUTPUT_FOLDER}/${EXOME}_topmotifs.fasta"

    echo ${FASTA_FILE}
    echo ${OUTFILE}
    echo ${PATTERN}
    grep -E -B 1 --no-group-separator "${PATTERN}" "${FASTA_FILE}" > "${OUTFILE}"

    # cleanup
    rm -f "${MOTIFS_COUNT}"
done