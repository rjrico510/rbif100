#!/bin/bash
./copyExomes.sh clinical_data.txt exomes exomesCohort
./createCrisprReady.sh motif_list.txt exomesCohort
./identifyCrisprSite.sh exomesCohort
./editGenome.sh exomesCohort
python3 exomeReport.py clinical_data.txt exomesCohort