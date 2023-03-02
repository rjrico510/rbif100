#!/bin/bash -xe
time python3 pipeline.py ../data/tinytest/tiny.fastq ../data/tinytest/tinysample.txt ../data/tinytest/tinyref.fa --fastqs-dir ../analysis/tinytest/fastqs --bams-dir ../analysis/tinytest/bams --report ../analysis/tinytest/report.txt --reindex --force --savesam --debug
WORKINGDIR="$(pwd)"
ANALYSIS=tinytest
cd ../analysis/${ANALYSIS}/fastqs
md5sum *.fastq > ../../md5sum_${ANALYSIS}_fastqs.txt
diff ../../md5sum_${ANALYSIS}_fastqs.txt ../../md5sum_${ANALYSIS}_fastqs_baseline.txt
cd "${WORKINGDIR}"
diff ../analysis/${ANALYSIS}/report.txt ../analysis/${ANALYSIS}/report.txt.baseline