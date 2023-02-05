#!/bin/bash
WORKING_DIR=$(pwd)
cd ../analysis/assignment/exomesCohort
md5sum *.fasta > ../md5sum.txt

cd ${WORKING_DIR}

cd ../analysis/assignment_python/exomesCohort
md5sum *.fasta > ../md5sum.txt

cd ${WORKING_DIR}
diff ../analysis/assignment/md5sum.txt ../analysis/assignment_python/md5sum.txt