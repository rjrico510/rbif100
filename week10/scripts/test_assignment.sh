#!/bin/bash -xe
DATA=assignment
cd ../analysis/${DATA}
md5sum *.pdf clinical_data_with_diversity.txt > md5sum.txt
cd -
diff ../analysis/${DATA}/baseline/md5sum.txt ../analysis/${DATA}/md5sum.txt