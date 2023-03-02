#!/bin/bash
cd ../analysis/assignment
md5sum MC1R* > md5sum.txt
cd -
diff ../analysis/assignmentmd5sum.txt ../analysis/assignment/baseline/md5sum.txt
