#!/bin/bash -xe
DATA=assignment
python3 pipeline.py ../data/${DATA}/clinical_data.txt ../data/${DATA}/diversityScores ../data/${DATA}/distanceFiles -o ../analysis/${DATA} -c clinical_data_with_diversity.txt -l ../analysis/${DATA}/pipeline.log -v -f