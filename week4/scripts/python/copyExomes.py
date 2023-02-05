#!/usr/bin/env python3

import argparse
import csv
import os
import shutil

DEFAULT_COHORT_DIR = "exomesCohort"
DEFAULT_UPPER = 30
DEFAULT_LOWER = 20

HEADER_DIAMETER = "Diamater (mm)"
HEADER_STATUS = "Status"
HEADER_CODENAME = "code_name"

SEQ_FLAG = "Sequenced"

def main():
    """main
    """
    parser = argparse.ArgumentParser(description="get exomes with specified diameter range")
    parser.add_argument("clinical_txt", help="clinical file")
    parser.add_argument("exome_dir", help="exome folder")
    parser.add_argument("-o", "--output-dir", dest="output_dir", default=DEFAULT_COHORT_DIR, help="directory to copy fastas")
    parser.add_argument("-l", "--lower-bound", dest="lower_bound", type=int, default=DEFAULT_LOWER, help="lower bound (inclusive)")
    parser.add_argument("-u", "--upper-bound", dest="upper_bound", type=int, default=DEFAULT_UPPER, help="upper bound (inclusive)")
    args = parser.parse_args()

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    with open(args.clinical_txt) as f:
        dialect = csv.Sniffer().sniff(f.read(1024))
        f.seek(0)
        reader = csv.DictReader(f, dialect=dialect)
        for line in reader:
            msg = f"{line[HEADER_CODENAME]}: {line[HEADER_DIAMETER]} {line[HEADER_STATUS]}"
            diameter = int(line[HEADER_DIAMETER])
            if args.lower_bound <= diameter <= args.upper_bound and line[HEADER_STATUS] == SEQ_FLAG:
                code_name = line[HEADER_CODENAME]
                msg += " MATCH"
                src = os.path.join(args.exome_dir, f"{code_name}.fasta")
                dest = os.path.join(args.output_dir, f"{code_name}.fasta")
                shutil.copy(src, dest)
            print(msg)


if __name__ == "__main__":
    main()