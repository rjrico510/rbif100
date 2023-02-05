#!/bin/bash
./copyExomes.sh clinical_data.txt exomes exomesCohort
./createCrisprReady.sh motif_list.txt exomesCohort CrisprReady
./identifyCrisprSite.sh CrisprReady PreCrispr
./editGenome.sh PreCrispr PostCrispr
python3 exomeReport.py clinical_data.txt PostCrispr