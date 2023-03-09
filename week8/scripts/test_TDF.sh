#!/bin/bash -xe
cd ../analysis/tdf
md5sum TDF* > md5sum.txt
cd -
diff ../analysis/tdf/md5sum.txt ../analysis/tdf/baseline/md5sum.txt
