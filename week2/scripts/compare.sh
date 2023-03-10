#!/bin/bash -xe
# generate checksums
cd ../analysis/assignment/motifs
md5sum *.fasta > ../md5sum_motifs.txt
cd -
cd ../analysis/assignment_python/motifs
md5sum *.fasta > ../md5sum_motifs.txt
cd -

# compare the bash and python results
diff ../analysis/assignment/motif_count.txt ../analysis/assignment_python/motif_count.txt
diff ../analysis/assignment/md5sum_motifs.txt ../analysis/assignment_python/md5sum_motifs.txt