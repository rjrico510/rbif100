#!/bin/bash -xe
DATA=tinytest
cd ../analysis/${DATA}
md5sum addax_distance.png badger_distance.png clinical_data_with_diversity.txt > md5sum.txt
cd -
diff ../analysis/${DATA}/md5sum_baseline.txt ../analysis/${DATA}/md5sum.txt