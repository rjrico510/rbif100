#!/bin/bash -xe
time python3 pipeline.py ../data/tiny0vartest/tiny0var.fastq ../data/tiny0vartest/tiny0varsample.txt ../data/tiny0vartest/tinyref.fa --fastqs-dir ../analysis/tiny0vartest/fastqs --bams-dir ../analysis/tiny0vartest/bams --report ../analysis/tiny0vartest/report.txt --reindex --force --savesam
WORKINGDIR="$(pwd)"
ANALYSIS=tiny0vartest
cd ../analysis/${ANALYSIS}/fastqs
md5sum *.fastq > ../../md5sum_${ANALYSIS}_fastqs.txt
diff ../../md5sum_${ANALYSIS}_fastqs.txt ../../md5sum_${ANALYSIS}_fastqs_baseline.txt
cd "${WORKINGDIR}"
diff ../analysis/${ANALYSIS}/report.txt ../analysis/${ANALYSIS}/report.txt.baseline