#!/usr/bin/env python3

import argparse
import collections
import os
import re

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
    parser = argparse.ArgumentParser(description="Insert base before PAM")
    parser.add_argument("fasta_dir", help="fasta directory")
    parser.add_argument("output_dir", help="output directory")
    parser.add_argument("--base", help="fasta directory", default="A")
    args = parser.parse_args()

    os.makedirs(args.output_dir)
    
    fasta_filenames = [f for f in os.listdir(args.fasta_dir) if f.endswith(".fasta")]
    regex = re.compile(r'([ACTG]{20})([ACTG]GG)')

    for fasta_filename in fasta_filenames:
        print(f"fasta: {fasta_filename}")
        # setup
        fasta_file = os.path.join(args.fasta_dir, fasta_filename)
        exome_name = fasta_filename.split("_")[0]
        output_file = os.path.join(args.output_dir, f"{exome_name}_postcrispr.fasta")

        with open(fasta_file) as f, open(output_file, "w") as fo:
            entry_gen = get_fasta_entry(f)
            for entry in entry_gen:
                seq = regex.sub(r"\1{}\2".format(args.base), entry.seq)
                fo.write(entry.desc)
                fo.write(seq)

if __name__ == "__main__":
    main()