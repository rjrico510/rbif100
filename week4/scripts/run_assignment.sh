#!/bin/bash
./copyExomes.sh ../data/assignment/clinical_data.txt ../data/assignment/exomes ../analysis/assignment/exomesCohort > ../analysis/assignment/copyExomes.txt
./createCrisprReady.sh ../data/assignment/motif_list.txt ../analysis/assignment/exomesCohort > ../analysis/assignment/createCrisprReady.txt
./identifyCrisprSite.sh ../analysis/assignment/exomesCohort > ../analysis/assignment/identifyCrisprSite.txt
./editGenome.sh ../analysis/assignment/exomesCohort > ../analysis/assignment/editGenome.txt
python3 exomeReport.py ../data/assignment/clinical_data.txt ../analysis/assignment/exomesCohort --report ../analysis/assignment/exomeReport.txt --force