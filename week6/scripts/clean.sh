#!/bin/bash -xe
# cleanup a test by name
NAME=$1
rm -f ../data/${NAME}/*.fa.*
rm -rf ../analysis/${NAME}/bams
rm -rf ../analysis/${NAME}/fastqs
rm -f ../analysis/${NAME}/report.txt
rm -f ../analysis/md5sum_${NAME}_fastqs.txt
rm -f tmp_${NAME}.txt


