#!/bin/bash -xe
WORKDIR="../analysis/${1}"
rm -f ${WORKDIR}/*.pdf
rm -f ${WORKDIR}/*.log
rm -f ${WORKDIR}/*.csv
rm -f ${WORKDIR}/clinical_data_with_diversity.txt
rm -f ${WORKDIR}/md5sum.txt