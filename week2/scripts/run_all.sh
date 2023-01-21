#!/bin/bash
# generate all data

# test
./week2.sh ../data/test/test1.fa ../data/test/test1_motifs.txt ../analysis/test/motifs ../analysis/test/motif_count.txt

# assignment (bash)
./week2.sh ../data/assignment/r_bifella.fasta ../data/assignment/interesting_motifs.txt ../analysis/assignment/motifs ../analysis/assignment/motif_count.txt

# assignment (python)
cd python || exit
python3 week2.py ../../data/assignment/r_bifella.fasta ../../data/assignment/interesting_motifs.txt -d ../../analysis/assignment_python/motifs -c ../../analysis/assignment_python/motif_count.txt
cd ..