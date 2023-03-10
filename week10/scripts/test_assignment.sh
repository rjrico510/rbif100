#!/bin/bash -xe
DATA=assignment
cd ../analysis/${DATA}
md5sum buffalo_distance.png fox_distance.png lion_distance.png clinical_data_with_diversity.txt > md5sum.txt
cd -
diff ../analysis/${DATA}/md5sum_baseline.txt ../analysis/${DATA}/md5sum.txt