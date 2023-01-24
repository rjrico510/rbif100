#!/usr/bin/env python3

import argparse
import csv
import os
import shutil

DEFAULT_COHORT_DIR = "exomesCohort"
DEFAULT_UPPER = 30
DEFAULT_LOWER = 20

HEADER_DIAMETER = "Diamater (mm)"
HEADER_CODENAME = "code_name"

def main():
    """main
    """
    parser = argparse.ArgumentParser(description="get exomes with specified diameter range")
    parser.add_argument("clinical_txt", help="clinical file")
    parser.add_argument("exome_dir", help="text file of motifs to search for")
    parser.add_argument("-o", "--output-dir", dest="output_dir", default=DEFAULT_COHORT_DIR, help="directory to copy fastas")
    parser.add_argument("-l", "--lower-bound", dest="lower_bound", type=int, default=DEFAULT_LOWER, help="lower bound (inclusive)")
    parser.add_argument("-u", "--upper-bound", dest="upper_bound", type=int, default=DEFAULT_UPPER, help="upper bound (inclusive)")
    args = parser.parse_args()

    os.makedirs(args.output_dir)

    with open(args.clinical_txt) as f:
        dialect = csv.Sniffer().sniff(f.read(1024))
        f.seek(0)
        reader = csv.DictReader(f, dialect=dialect)
        for line in reader:
            print(f"{line[HEADER_CODENAME]}: {line[HEADER_DIAMETER]}")
            diameter = int(line[HEADER_DIAMETER])
            if args.lower_bound <= diameter <= args.upper_bound:
                code_name = line[HEADER_CODENAME]
                print(f"{code_name} MATCH")
                src = os.path.join(args.exome_dir, f"{code_name}.fasta")
                dest = os.path.join(args.output_dir, f"{code_name}.fasta")
                shutil.copy(src, dest)

if __name__ == "__main__":
    main()