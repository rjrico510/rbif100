#!/bin/bash
./copyExomes.sh ../data/assignment/clinical_data.txt ../data/assignment/exomes ../analysis/assignment/exomesCohort > ../analysis/assignment/copyExomes.txt
./createCrisprReady.sh ../data/assignment/motif_list.txt ../analysis/assignment/exomesCohort ../analysis/assignment/CrisprReady > ../analysis/assignment/createCrisprReady.txt