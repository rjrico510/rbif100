# RBIF100 Assignment 1 (Week 2)

 Author: Rudy Rico

 email: rrico@brandeis.edu

 github: https://github.com/rjrico510/rbif100/tree/main/week2

 Goals: given a list of motifs and a fasta file, write a bash script which produces:
 - file containing the number of times each motif is present.
 - folder of fasta files (1 per motif) which include only the entry for a given motif.

 Usage:
 `./motif_counter.sh fasta_file motifs_file`

 Note: the script will take two optional positional parameters - name of the motifs folder, and the name of the motif count file.

 Assumptions:
 - The motifs file is a text file with exactly 1 motif per line
 - The fasta file does not split the sequence portion via line feeds, i.e. the entire sequence is on one line.
 - A motif counts per occurrence, not simply per sequence (e.g. sequence ATAT containts motif AT twice)

 Contents:
 - README.md (this file)
 - motif_counter.sh - the script which finds the motifs and generates the results
 - data - the two input files for the assignment
 - analysis - the results of the assignment
 - run.sh - the actual command use to run the data in this layout

 Notes:
 The linked git repository includes:
 - all of the above
 - a python implementation to verify the result
 - a tiny test dataset