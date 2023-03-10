#!/bin/bash -xe
time python3 pipeline.py ../data/assignment/hawkins_pooled_sequences.fastq.gz ../data/assignment/harrington_clinical_data.txt ../data/assignment/dgorgon_reference.fa --fastqs-dir ../analysis/assignment/fastqs --bams-dir ../analysis/assignment/bams --report ../analysis/assignment/report.txt --reindex --force
WORKINGDIR="$(pwd)"
ANALYSIS=assignment
cd ../analysis/${ANALYSIS}/fastqs
md5sum *.fastq > ../../md5sum_${ANALYSIS}_fastqs.txt
diff ../../md5sum_${ANALYSIS}_fastqs.txt ../../md5sum_${ANALYSIS}_fastqs_baseline.txt
cd "${WORKINGDIR}"
diff ../analysis/${ANALYSIS}/report.txt ../analysis/${ANALYSIS}/report.txt.baseline
