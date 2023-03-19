#!/bin/bash -xe
DATA=alldata
python3 pipeline.py ../data/${DATA}/clinical_data.txt ../data/${DATA}/diversityScores ../data/${DATA}/distanceFiles -o ../analysis/${DATA} -c clinical_data_with_diversity.txt -m 50 -n 0 -l ../analysis/${DATA}/pipeline.log -f