#!/bin/bash
python3 copyExomes.py ../../data/assignment/clinical_data.txt ../../data/assignment/exomes -o ../../analysis/assignment_python/exomesCohort > ../../analysis/assignment_python/copyExomes.txt
python3 createCrisprReady.py ../../analysis/assignment_python/exomesCohort ../../data/assignment/motif_list.txt -o ../../analysis/assignment_python/TopMotifs > ../../analysis/assignment_python/createCrisprReady.txt
python3 identifyCrisprSite.py ../../analysis/assignment_python/TopMotifs -o ../../analysis/assignment_python/PreCrispr > ../../analysis/assignment_python/identifyCrisprSite.txt
python3 editGenome.py ../../analysis/assignment_python/PreCrispr -o ../../analysis/assignment_python/PostCrispr > ../../analysis/assignment_python/editGenome.txt
python3 ../exomeReport.py ../../data/assignment/clinical_data.txt ../../analysis/assignment_python/PostCrispr --report ../../analysis/assignment_python/exomeReport.txt --force