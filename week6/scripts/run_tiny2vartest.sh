#!/bin/bash -xe
time python3 pipeline.py ../data/tiny2vartest/tiny2var.fastq ../data/tiny2vartest/tiny2varsample.txt ../data/tiny2vartest/tinyref.fa --fastqs-dir ../analysis/tiny2vartest/fastqs --bams-dir ../analysis/tiny2vartest/bams --report ../analysis/tiny2vartest/report.txt --reindex --force --savesam
WORKINGDIR="$(pwd)"
ANALYSIS=tiny2vartest
cd ../analysis/${ANALYSIS}/fastqs
md5sum *.fastq > ../../md5sum_${ANALYSIS}_fastqs.txt
diff ../../md5sum_${ANALYSIS}_fastqs.txt ../../md5sum_${ANALYSIS}_fastqs_baseline.txt
cd "${WORKINGDIR}"
diff ../analysis/${ANALYSIS}/report.txt ../analysis/${ANALYSIS}/report.txt.baseline