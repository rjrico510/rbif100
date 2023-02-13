#!/usr/bin/env/python3
"""Pipeline to identify nucleotides responsible for each color of mold

Given a fastq file, reference fasta and a sample file:

Part 1: for each entry in the fastq file:
(1) assign each barcode to a sample
(2) trim the barcode
(3) trim the reads starting wth the first occurrence of consecutive D and/or F scores
(4) Write the trimmed read to a fastq file (by sample name) to a fastqs output folder

Part 2: Align each fastq to the reference usng bwa
(1) index the reference
(2) perform the alignment
(3) save each SAM file output to a bam folder

Part 3: convert each SAM to BAM
(1) within the bam folder, convert SAM to BAM
(2) sort the BAM
(3) remove the SAM and unsorted BAM files

Part 4: identify mutations using pysam
(1) Report all SNPs

Part 5: Generate report
(1) specify the color, the mutation responsible, wildtype and variant bases, and # sequences for each sample
e.g.
    The green mold was caused by a mutation in position 23. The wildtype base was A and the mutation was C.
    The black mold…

    Sample Tim had a green mold, 320 reads, and had 32% of the reads at position 23 had the mutation C. 
    Sample Kristen ...


inputs:
(1) sample file - tab-delimited file with headers: Name, Color, Barcode
(2) fastq - sequencing data with leading barcode
(3) fasta reference - reference sequence for alignment & variant calling

outputs:
(1) folder of fastqs
(2) folder of sorted bam files
(3) report (text file)
"""

import argparse
import csv
import gzip
import os
import pysam
import pathlib
import re
import subprocess
import sys

# sample file headers
SAMPLE_HEADER_NAME = "Name"
SAMPLE_HEADER_COLOR = "Color"
SAMPLE_HEADER_BC = "Barcode"


#
# The following code is taken from the week6 necessary_scripts folder
#

class ParseFastQ(object):
    """Returns a read-by-read fastQ parser analogous to file.readline()"""
    def __init__(self,filePath,headerSymbols=['@','+']):
        """Returns a read-by-read fastQ parser analogous to file.readline().
        Exmpl: parser.next()
        -OR-
        Its an iterator so you can do:
        for rec in parser:
            ... do something with rec ...
 
        rec is tuple: (seqHeader,seqStr,qualHeader,qualStr)
        """
        if filePath.endswith('.gz'):
            self._file = gzip.open(filePath, 'rt')
        else:
            self._file = open(filePath, 'r')
        self._currentLineNumber = 0
        self._hdSyms = headerSymbols
         
    def __iter__(self):
        return self
     
    def __next__(self):
        """Reads in next element, parses, and does minimal verification.
        Returns: tuple: (seqHeader,seqStr,qualHeader,qualStr)"""
        # ++++ Get Next Four Lines ++++
        elemList = []
        for i in range(4):
            line = self._file.readline()
            self._currentLineNumber += 1 ## increment file position
            if line:
                elemList.append(line.strip('\n'))
            else: 
                elemList.append(None)
         
        # ++++ Check Lines For Expected Form ++++
        trues = [bool(x) for x in elemList].count(True)
        nones = elemList.count(None)
        # -- Check for acceptable end of file --
        if nones == 4:
            raise StopIteration
        # -- Make sure we got 4 full lines of data --
        assert trues == 4,\
               "** ERROR: It looks like I encountered a premature EOF or empty line.\n\
               Please check FastQ file near line number %s (plus or minus ~4 lines) and try again**" % (self._currentLineNumber)
        # -- Make sure we are in the correct "register" --
        assert elemList[0].startswith(self._hdSyms[0]),\
               "** ERROR: The 1st line in fastq element does not start with '%s'.\n\
               Please check FastQ file near line number %s (plus or minus ~4 lines) and try again**" % (self._hdSyms[0],self._currentLineNumber) 
        assert elemList[2].startswith(self._hdSyms[1]),\
               "** ERROR: The 3rd line in fastq element does not start with '%s'.\n\
               Please check FastQ file near line number %s (plus or minus ~4 lines) and try again**" % (self._hdSyms[1],self._currentLineNumber) 
        # -- Make sure the seq line and qual line have equal lengths --
        assert len(elemList[1]) == len(elemList[3]), "** ERROR: The length of Sequence data and Quality data of the last record aren't equal.\n\
               Please check FastQ file near line number %s (plus or minus ~4 lines) and try again**" % (self._currentLineNumber) 
         
        # ++++ Return fatsQ data as tuple ++++
        return tuple(elemList)

#
# The following code is taken from the week6 necessary_scripts folder
#

def pileup(indexed_bam_file):
    #test file, replaced with the sorted.bam you are using. Make sure it is indexed! (Use samtools index yourbam.sorted.bam)
    samfile = pysam.AlignmentFile(indexed_bam_file, "rb")

    #Since our reference only has a single sequence, we're going to pile up ALL of the reads. Usually you would do it in a specific region (such as chromosome 1, position 1023 to 1050 for example)
    for pileupcolumn in samfile.pileup():
        print ("coverage at base %s = %s" % (pileupcolumn.pos, pileupcolumn.n))
        #use a dictionary to count up the bases at each position
        ntdict = {}
        for pileupread in pileupcolumn.pileups:
            if not pileupread.is_del and not pileupread.is_refskip:
                # You can uncomment the below line to see what is happening in the pileup. 
                # print ('\tbase in read %s = %s' % (pileupread.alignment.query_name, pileupread.alignment.query_sequence[pileupread.query_position]))
                base = pileupread.alignment.query_sequence[pileupread.query_position]
                ########## ADD ADDITIONAL CODE HERE ############# 
                # Populate the ntdict with the counts of each base 
                # This dictionary will hold all of the base read counts per nucletoide per position.
                # Use the dictionary to calculate the frequency of each site, and report it if if the frequency is NOT  100% / 0%. 
                #############################################
        print (ntdict)
    samfile.close()


def parse_arguments() -> argparse.Namespace:
    """Parses input arguments

    Returns:
        argparse.Namespace: argument object
    """

    REPORT_DEFAULT = "report.txt"
    FASTQS_DEFAULT = "fastqs"
    BAMS_DEFAULT = "bams"

    parser = argparse.ArgumentParser("Demultiplex and trim reads by barcode")
    parser.add_argument("fastq", help = "barcoded fastq sequence data")
    parser.add_argument("samples", help = "tab-delimited sample file")
    parser.add_argument("reference", help = "fasta reference")
    parser.add_argument("--fastqs-dir",  dest="fastqs_dir", help="output fastq folder", default=FASTQS_DEFAULT)
    parser.add_argument("--bams-dir",  dest="bams_dir", help="output bam folder", default=BAMS_DEFAULT)
    parser.add_argument("--report",  help="output fastq folder", default=REPORT_DEFAULT)
    parser.add_argument("--force", action="store_true", help="overwrite outputs")
    args = parser.parse_args()

    # echo inputs
    print(f"sequencing fastq: {args.fastq}")
    print(f"sample file: {args.samples}")
    print(f"reference fasta: {args.reference}")
    print(f"fastqs dir: {args.fastqs_dir}")
    print(f"bams dir: {args.bams_dir}")
    print(f"report file: {args.report}")
    print(f"force: {args.force}")

    #
    # input/output validation
    #

    # check input existence
    for input_file in [args.fastq, args.samples, args.reference]:
        if not os.path.exists(input_file):
            print(f"{input_file} not found.  Exiting...")
            sys.exit(1)

    # don't overwrite existing intermediates/outputs unless forced
    for output in [args.fastqs_dir, args.bams_dir, args.report]:
        if os.path.exists(output):
            if not args.force:
                print(f"{output} already exists.  Use --force to overwrite.  Exiting...")
                sys.exit(2)
            else:
                print(f"Deleting existing {output} ...")
                if os.path.isdir(output):
                    rm_tree(output)
                else:
                    pathlib.Path(output).unlink()

    return args


def verify_prequisites():
    """Verify required third-party applications are present
    """
    for app in ["bwa", "samtools"]:
        cmd = ["which", app]
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError:
            print("{}: not found .. exiting")
            sys.exit(3)
            

def create_fastqs(sample_file: str, fastq_file: str, fastqs_dir: str) -> None:
    """demultplex a fastq by barcode; trim barcodes and low-quality bases
       (1st occurrence of consecutive D/F quality scores)
       and write the new per-barcode fastqs named <name>_trimmed.fastq
       to the output folder. (name = Name field from sample file)
    
       - Assumes barcodes are of the same length - will raise an exception otherwise
       - Assumes barcodes start at the beginning of the read
       - Skips barcodes with no assigned name

    Args:
        sample_file (str): tab-delimited file of sample name, color and barcode
        fastq_file (str): fastqs input sequence data
        fastqs_dir (str): output folder of fastqs
    """

    regex = re.compile(r'[DF]{2}') # low quality
    SEQHEADER = 0
    SEQ = 1
    QUALHEADER = 2
    QUAL = 3

    # setup
    bc_name = {}
    with open(sample_file) as f:
        dialect = csv.Sniffer().sniff(f.read(1024))
        f.seek(0)
        reader = csv.DictReader(f, dialect=dialect)
        bc_lengths = set()
        for line in reader:
            bc_name[line[SAMPLE_HEADER_BC]] = line[SAMPLE_HEADER_NAME]
            bc_lengths.add(len(line[SAMPLE_HEADER_BC]))

        if len(bc_lengths) > 1:
            raise BCLengthException(f"{sample_file} has barcode lengths {','.join((str(bcl) for bcl in bc_lengths))}")

    bc_length = list(bc_lengths)[0]

    fastq_parser = ParseFastQ(fastq_file)
    os.makedirs(fastqs_dir)

    # parse sequence data one read at a time
    for read in fastq_parser:
        # get the barcode
        bc = read[SEQ][:bc_length]
        name = bc_name.get(bc)
        if name:
            # find low-quality bases
            match = regex.search(read[QUAL])
            end_pos = match.start() if match else None

            # trim
            if end_pos:
                seq_str = read[SEQ][bc_length:end_pos]
                qual_str = read[QUAL][bc_length:end_pos]
            else:
                seq_str = read[SEQ][bc_length:]
                qual_str = read[QUAL][bc_length:]
            filename = os.path.join(fastqs_dir, f"{name}_trimmed.fastq")

            # write read - append to existing
            # seems like a lot of I/O - might be a better way to do this
            with open(filename, "a+") as f:
                for read_line in (read[SEQHEADER], seq_str, read[QUALHEADER], qual_str):
                    f.write(f"{read_line}\n")
        else:
            print(f"barcode {bc} has no assigned sample ... skipping")


def align_reads(reference: str, fastqs_dir: str, bams_dir: str) -> None:
    """_summary_

    Args:
        reference (str): _description_
        fastqs_dir (str): _description_
        bams_dir (str): _description_
    """
    # index reference
    cmd = ["bwa", "index", reference]

def sam_to_bam(bams_dir: str) -> None:
    pass

def call_variants(bams_dir: str) -> dict:
    return {}

def generate_report(results: dict, report_file: str) -> None:
    pass


class BCLengthException(Exception):
    """exception if barcodes are not all the same length

    Args:
        Exception (Exception): exception
    """
    pass


#
# helper methods
#

def rm_tree(pth):
    """delete a directory and all contents
    https://stackoverflow.com/questions/50186904/pathlib-recursively-remove-directory

    using python 3 pathlib instead of shutil

    Args:
        pth (str): path to a directory
    """
    pth = pathlib.Path(pth)
    for child in pth.glob('*'):
        if child.is_file():
            child.unlink()
        else:
            rm_tree(child)
    pth.rmdir()

def main():
    """main
    """
    args = parse_arguments()
    create_fastqs(args.samples, args.fastq, args.fastqs_dir)
    align_reads(args.reference, args.fastqs_dir, args.bams_dir)
    sam_to_bam(args.bams_dir)
    results = call_variants(args.bams_dir)
    generate_report(results, args.report)


if __name__ == "__main__":
    main()