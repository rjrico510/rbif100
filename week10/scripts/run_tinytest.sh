#!/bin/bash -xe
DATA=tinytest
python3 pipeline.py ../data/${DATA}/clinical_data.txt ../data/${DATA}/diversityScores ../data/${DATA}/distanceFiles -o ../analysis/${DATA} -c ../analysis/${DATA}/clinical_data_with_diversity.txt -v -f