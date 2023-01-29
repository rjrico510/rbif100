#!/bin/bash
WORKING_DIR=$(pwd)
cd ../analysis/assignment/exomesCohort
md5sum *.fasta > ../md5sum_copyExomes.txt
cd ../CrisprReady
md5sum *.fasta > ../md5sum_CrisprReady.txt

cd ${WORKING_DIR}

cd ../analysis/assignment_python/exomesCohort
md5sum *.fasta > ../md5sum_copyExomes.txt
cd ../CrisprReady
md5sum *.fasta > ../md5sum_CrisprReady.txt

cd ${WORKING_DIR}
diff ../analysis/assignment/md5sum_copyExomes.txt ../analysis/assignment_python/md5sum_copyExomes.txt 
diff ../analysis/assignment/md5sum_CrisprReady.txt ../analysis/assignment_python/md5sum_CrisprReady.txt 