#!/bin/bash -xe
python3 pipeline.py ../data/assignment/hawkins_pooled_sequences.fastq ../data/assignment/harrington_clinical_data.txt ../data/assignment/dgorgon_reference.fa --fastqs-dir ../analysis/assignment/fastqs --bams-dir ../analysis/assignment/bams --report ../analysis/assignment/report.txt --force
WORKINGDIR="$(pwd)"
ANALYSIS=assignment
cd ../analysis/${ANALYSIS}/fastqs
md5sum *.fastq > ../../md5sum_${ANALYSIS}_fastqs.txt
diff ../../md5sum_${ANALYSIS}_fastqs.txt ../../md5sum_${ANALYSIS}_fastqs_baseline.txt
cd "${WORKINGDIR}"
