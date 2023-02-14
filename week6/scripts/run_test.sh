#!/bin/bash -xe
time python3 pipeline.py ../data/test/test.fastq ../data/test/test.txt ../data/test/dgorgon_reference.fa --fastqs-dir ../analysis/test/fastqs --bams-dir ../analysis/test/bams --report ../analysis/test/report.txt --reindex --force
WORKINGDIR="$(pwd)"
ANALYSIS=test
cd ../analysis/${ANALYSIS}/fastqs
md5sum *.fastq > ../../md5sum_${ANALYSIS}_fastqs.txt
diff ../../md5sum_${ANALYSIS}_fastqs.txt ../../md5sum_${ANALYSIS}_fastqs_baseline.txt
cd "${WORKINGDIR}"
diff ../analysis/${ANALYSIS}/report.txt ../analysis/${ANALYSIS}/report.txt.baseline