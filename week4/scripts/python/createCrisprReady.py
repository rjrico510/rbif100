#!/usr/bin/env python3

import argparse
import collections
import os

FASTA_OUTPUT_SUFFIX = "_topmotifs.fasta"

FastaEntry = collections.namedtuple("FastaEntry", ["desc", "seq"])

def get_fasta_entry(f):
    """Generator - produces a description and sequence line from a fasta

    Args:
        f (file handle): handle to fasta file

    Yields:
        FastaEntry: NamedTuple of desc and seq
    """
    desc = f.readline()
    while desc:
        seq = f.readline()
        result = FastaEntry(desc, seq)
        yield result
        desc = f.readline()

def main():
    """main
    """
    parser = argparse.ArgumentParser(description="Get sequences for top 3 motifs for each fasta in a folder")
    parser.add_argument("fasta_dir", help="fasta directory")
    parser.add_argument("motifs_file", help="text file of motifs to search for")
    parser.add_argument("--output-dir", dest="output_dir", help="output directory")
    args = parser.parse_args()

    if args.output_dir:
        output_dir = args.output_dir
        os.makedirs(output_dir)
    else:
        output_dir = args.fasta_dir

    motif_count = {}
    with open(args.motifs_file) as f:
        for motif in f:
            motif_count[motif.strip()] = 0
    
    fasta_filenames = [f for f in os.listdir(args.fasta_dir) if f.endswith(".fasta")]

    for fasta_filename in fasta_filenames:
        print(f"fasta: {fasta_filename}")
        # setup
        fasta_file = os.path.join(args.fasta_dir, fasta_filename)
        exome_name, _ = os.path.splitext(fasta_filename)
        output_file = os.path.join(output_dir, f"{exome_name}{FASTA_OUTPUT_SUFFIX}")
        count_file = os.path.join(output_dir, f"{exome_name}_motif_count.txt")

        with open(fasta_file) as f, open(output_file, "w") as fo, open(count_file, "w") as fc:
            # pass 1 - get the motif counts
            print("PASS 1 - get motif counts")
            entry_gen = get_fasta_entry(f)
            for entry in entry_gen:
                for motif in motif_count:
                    matches = entry.seq.count(motif)
                    if matches > 0:
                        motif_count[motif] += matches
    
            sorted_motifs = [v for v in sorted(motif_count.items(), key = lambda x:x[1], reverse=True)]
            top_motifs = [t[0] for t in sorted_motifs][0:3]
            print(sorted_motifs[0:3])

            # intermediate file - for debugging
            for motif, count in sorted_motifs:
                fc.write("{} {}\n".format(motif, count))



            # fasta pass 2 - write the fasta files for the top 3 motifs
            f.seek(0)
            print("PASS 2 - make fastas for top 3 counts")
            entry_gen = get_fasta_entry(f)
            for entry in entry_gen:
                for motif in top_motifs:
                    matches = entry.seq.count(motif)
                    if matches > 0:
                        fo.write(entry.desc)
                        fo.write(entry.seq)
                        break

        # cleanup - clear the motif dictionary
        motif_count = dict.fromkeys(motif_count, 0)

if __name__ == "__main__":
    main()