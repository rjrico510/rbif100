#!/usr/bin/env python3

import argparse
import collections
import os

DEFAULT_MOTIF_DIR = "motifs_py"
DEFAULT_MOTIF_COUNT = "motif_count_py.txt"

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
    parser = argparse.ArgumentParser(description="Count motifs in a fasta")
    parser.add_argument("fasta_file", help="fasta file")
    parser.add_argument("motifs_file", help="text file of motifs to search for")
    parser.add_argument("-d", "--motif-dir", dest="motif_dir", default=DEFAULT_MOTIF_DIR, help="directory to save motif fastas")
    parser.add_argument("-c", "--motif-count", dest="motif_count", default=DEFAULT_MOTIF_COUNT, help="file to save motif counts")
    args = parser.parse_args()

    os.makedirs(args.motif_dir)

    motif_count = collections.OrderedDict()
    motif_matches = collections.OrderedDict()

    with open(args.motifs_file) as f:
        for motif in f:
            motif_count[motif.strip()] = 0
            motif_matches[motif.strip()] = []
            
    with open(args.fasta_file) as f:
        entry_gen = get_fasta_entry(f)
        for entry in entry_gen:
            for motif in motif_count:
                matches = entry.seq.count(motif)
                if matches > 0:
                    motif_count[motif] += matches
                    motif_matches[motif].append(entry)
    
    with open(args.motif_count, "w") as f:
        for motif in motif_count:
            f.write("{} {}\n".format(motif, motif_count[motif]))

    for motif in motif_matches:
        with open(os.path.join(args.motif_dir, "{}.txt".format(motif)), "w") as f:
            for entry in motif_matches[motif]:
                f.write(entry.desc)
                f.write(entry.seq)

if __name__ == "__main__":
    main()