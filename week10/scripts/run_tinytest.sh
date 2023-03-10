#!/bin/bash -xe
DATA=tinytest
python3 pipeline.py ../data/${DATA}/clinical_data.txt ../data/${DATA}/diversityScores ../data/${DATA}/distanceFiles -o ../analysis/${DATA} -c clinical_data_with_diversity.txt -m 1 -n 1 -v -f