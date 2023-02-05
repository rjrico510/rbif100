#!/usr/bin/env python3
"""Generates report

Inputs:
- clinical data file - format:
    - tab-delimited
    - header:
    Discoverer	Location	Diamater (mm)	Environment	Status	code_name
    (string)      (string)    (int)           (string)    (string)(string)
    - Status is either "Sequenced" or "not sequenced" - former string is a match
    - code_name must match a fasta in the exome folder, e.g.there must be a code_name.fasta
- directory of fasta files named "<code_name>_postcrispr.fasta" (where code_name matches the clinical file)

Outputs:
- report of the following format
-- header portion taken from the clinical data file (only include fastas with a matching code_name)
-- union of all genes (count and list)

Example of Report:

Organism CODENAME, discovered by DISCOVERER, has a diameter of DIAMETER, and from the environment ENVIRONMENT.

..

...

The number of the union of genes across the cohort is ____. Those genes are:
GENE1,GENE30,GENE50,etc.

"""

import argparse
import csv
import os
import sys

REPORT_DEFAULT = "exomeReport.txt"

HEADER_DIAMETER = "Diamater (mm)"
HEADER_STATUS = "Status"
HEADER_CODENAME = "code_name"
HEADER_DISCOVERER = "Discoverer"
HEADER_ENVIRONMENT = "Environment"

FASTA_SUFFIX = "_postcrispr.fasta"

def main():
    """main
    """
    parser = argparse.ArgumentParser("Exome Cohort report")
    parser.add_argument("clinical_txt", help = "clinical data file")
    parser.add_argument("exome_dir", help = "Post-processed CRISPR data directory")
    parser.add_argument("--report",  help="report file", default=REPORT_DEFAULT)
    parser.add_argument("--force", action="store_true", help="overwrite existing")
    args = parser.parse_args()

    # don't overwrite an existing report unless you really want to
    if os.path.exists(args.report) and not args.force:
        print(f"{args.report} already exists ... use --force to overwrite.    Exiting...")
        sys.exit(1)

    # get all the exomes present from the fasta names
    fasta_filenames = [f for f in os.listdir(args.exome_dir) if f.endswith(FASTA_SUFFIX)]
    exomes = [f.split("_")[0] for f in fasta_filenames]


    with  open(args.report, 'w') as fo:

        # generate the summary section - report exomes
        with open(args.clinical_txt) as f:
            dialect = csv.Sniffer().sniff(f.read(1024))
            f.seek(0)
            reader = csv.DictReader(f, dialect=dialect)
            for line in reader:
                if line[HEADER_CODENAME] in exomes:
                    msg = f"Organism {line[HEADER_CODENAME]}, discovered by {line[HEADER_DISCOVERER]}, has a diameter of {line[HEADER_DIAMETER]}, and is from the environment {line[HEADER_ENVIRONMENT]}\n"
                    fo.write(msg)

        # print the union of all genes present in the cohort
        # - get list of all genes - iterate through all files
        genes = set()
        for fasta_filename in fasta_filenames:
            with open(os.path.join(args.exome_dir, fasta_filename)) as ff:
                for line in ff:
                    if line.startswith(">"):
                        genes.add(line.strip()[1:])
        num_genes = len(genes)

        # - print to summary (sort the list)
        gene_list = [(g, int(g.replace("gene", ""))) for g in genes]
        gene_list = [g[0] for g in sorted(gene_list, key=lambda x: x[1])]

        all_genes = ','.join(gene_list)
        fo.write(f"The number of the union of genes across the cohort is {num_genes}.  Those genes are:\n")
        fo.write(f"{all_genes}\n")


if __name__ == "__main__":
    main()