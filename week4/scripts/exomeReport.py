#!/usr/bin/env python3
"""Generates report

Example:

Organism FOX, discovered by DISCOVERER, has a diameter of DIAMETER, and from the environment ENVIRONMENT.

..

...

The number of the union of genes across the cohort is ____. Those genes are:
GENE1,GENE30,GENE50,etc.

"""

import argparse
import csv
import os

REPORT_DEFAULT = "exomeReport.txt"

HEADER_DIAMETER = "Diamater (mm)"
HEADER_STATUS = "Status"
HEADER_CODENAME = "code_name"
HEADER_DISCOVERER = "Discoverer"
HEADER_ENVIRONMENT = "Environment"

def main():
    """main
    """
    parser = argparse.ArgumentParser("Exome Cohort report")
    parser.add_argument("clinical_txt", help = "clinical data file")
    parser.add_argument("exome_dir", help = "Post-processed CRISPR data directory")
    parser.add_argument("--report",  help="report file", default=REPORT_DEFAULT)
    args = parser.parse_args()

    # get all the exomes present from the fasta names
    fasta_filenames = [f for f in os.listdir(args.exome_dir) if f.endswith(".fasta")]
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