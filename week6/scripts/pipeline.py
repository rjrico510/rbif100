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
import collections
import csv
import gzip
import os
import pysam
import pathlib
import re
import subprocess
import sys
import typing

TRIMMED_FASTQ = "_trimmed.fastq"
SORTED_BAM = "_sorted.bam"

#
# class & exception definitions
#


class SampleFile:
    """representation of sample file"""

    SAMPLE_HEADER_NAME = "Name"
    SAMPLE_HEADER_COLOR = "Color"
    SAMPLE_HEADER_BC = "Barcode"

    def __init__(self, sample_file):
        """constructor

        Parses the file and saves some fields about the data.
        Assumes the file isn't very big.

        Args:
            sample_file (str): sample file path

        Raises:
            BCLengthException: if there is more than 1 barcode length
        """
        self._bc_name = {}
        self._name_color = {}
        self._color_names = collections.defaultdict(list)
        with open(sample_file) as f:
            dialect = csv.Sniffer().sniff(f.read(1024))
            f.seek(0)
            reader = csv.DictReader(f, dialect=dialect)
            bc_lengths = set()
            for line in reader:
                self._name_color[line[self.SAMPLE_HEADER_NAME]] = line[
                    self.SAMPLE_HEADER_COLOR
                ]
                self._color_names[line[self.SAMPLE_HEADER_COLOR]].append(
                    line[self.SAMPLE_HEADER_NAME]
                )
                self._bc_name[line[self.SAMPLE_HEADER_BC]] = line[
                    self.SAMPLE_HEADER_NAME
                ]
                bc_lengths.add(len(line[self.SAMPLE_HEADER_BC]))

            if len(bc_lengths) > 1:
                raise BCLengthException(
                    f"{sample_file} has barcode lengths {','.join((str(bcl) for bcl in bc_lengths))}"
                )

        self._bc_length = list(bc_lengths)[0]

    @property
    def bc_length(self):
        return self._bc_length

    @property
    def bc_name(self):
        return self._bc_name

    @property
    def name_color(self):
        return self._name_color

    @property
    def color_names(self):
        return self._color_names


class BCLengthException(Exception):
    """exception if barcodes are not all the same length

    Args:
        Exception (Exception): exception
    """

    pass


class VariantFrequency(typing.NamedTuple):
    """representation of a variant position"""

    position: int
    nreads: int
    wildtype: str
    mutation: str
    frequencies: tuple


#
# code from the week6 necessary_scripts folder
#


class ParseFastQ(object):
    """Returns a read-by-read fastQ parser analogous to file.readline()"""

    def __init__(self, filePath, headerSymbols=["@", "+"]):
        """Returns a read-by-read fastQ parser analogous to file.readline().
        Exmpl: parser.next()
        -OR-
        Its an iterator so you can do:
        for rec in parser:
            ... do something with rec ...

        rec is tuple: (seqHeader,seqStr,qualHeader,qualStr)
        """
        if filePath.endswith(".gz"):
            self._file = gzip.open(filePath, "rt")
        else:
            self._file = open(filePath, "r")
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
            self._currentLineNumber += 1  ## increment file position
            if line:
                elemList.append(line.strip("\n"))
            else:
                elemList.append(None)

        # ++++ Check Lines For Expected Form ++++
        trues = [bool(x) for x in elemList].count(True)
        nones = elemList.count(None)
        # -- Check for acceptable end of file --
        if nones == 4:
            raise StopIteration
        # -- Make sure we got 4 full lines of data --
        assert trues == 4, (
            "** ERROR: It looks like I encountered a premature EOF or empty line.\n\
               Please check FastQ file near line number %s (plus or minus ~4 lines) and try again**"
            % (self._currentLineNumber)
        )
        # -- Make sure we are in the correct "register" --
        assert elemList[0].startswith(self._hdSyms[0]), (
            "** ERROR: The 1st line in fastq element does not start with '%s'.\n\
               Please check FastQ file near line number %s (plus or minus ~4 lines) and try again**"
            % (self._hdSyms[0], self._currentLineNumber)
        )
        assert elemList[2].startswith(self._hdSyms[1]), (
            "** ERROR: The 3rd line in fastq element does not start with '%s'.\n\
               Please check FastQ file near line number %s (plus or minus ~4 lines) and try again**"
            % (self._hdSyms[1], self._currentLineNumber)
        )
        # -- Make sure the seq line and qual line have equal lengths --
        assert len(elemList[1]) == len(elemList[3]), (
            "** ERROR: The length of Sequence data and Quality data of the last record aren't equal.\n\
               Please check FastQ file near line number %s (plus or minus ~4 lines) and try again**"
            % (self._currentLineNumber)
        )

        # ++++ Return fatsQ data as tuple ++++
        return tuple(elemList)


def pileup(indexed_bam_file: str) -> list:
    """Generate pileup and identify positons where > 1 base is present

    Iterate through the columns of a pileup, and count the number of bases of each type at each position.
    If more than one base is observed, create a tuple of position, # reads, & base frequency
    and add it to a list of such tuples

    Args:
        indexed_bam_file (str): path to indexed bam file

    Returns:
        list: tuples (position, # reads, frequencies)
    """
    samfile = pysam.AlignmentFile(indexed_bam_file, "rb")
    variants = []

    # Since our reference only has a single sequence, we're going to pile up ALL of the reads. Usually you would do it in a specific region (such as chromosome 1, position 1023 to 1050 for example)
    for pileupcolumn in samfile.pileup():
        print("coverage at base %s = %s" % (pileupcolumn.pos, pileupcolumn.n))
        # use a dictionary to count up the bases at each position (auto-intialized to 0)
        ntdict = collections.defaultdict(int)
        for pileupread in pileupcolumn.pileups:
            if not pileupread.is_del and not pileupread.is_refskip:
                # You can uncomment the below line to see what is happening in the pileup.
                # print ('\tbase in read %s = %s' % (pileupread.alignment.query_name, pileupread.alignment.query_sequence[pileupread.query_position]))
                base = pileupread.alignment.query_sequence[pileupread.query_position]
                # Populate the ntdict with the counts of each base
                # This dictionary will hold all of the base read counts per nucletoide per position.
                # Use the dictionary to calculate the frequency of each site, and report it if if the frequency is NOT  100% / 0%.
                ntdict[base] += 1
        print(ntdict)
        if len(ntdict) > 1:  # found more than 1 base at the position
            # need position, count, and base frequency
            frequencies = [
                (base, ntdict[base] / pileupcolumn.n) for base in ["A", "C", "T", "G"]
            ]
            variants.append((pileupcolumn.pos, pileupcolumn.n, tuple(frequencies)))

    samfile.close()

    return variants


#
# top-level functions
#


def parse_arguments() -> argparse.Namespace:
    """Parses input arguments

    Returns:
        argparse.Namespace: argument object
    """

    REPORT_DEFAULT = "report.txt"
    FASTQS_DEFAULT = "fastqs"
    BAMS_DEFAULT = "bams"

    parser = argparse.ArgumentParser(
        description="Demultiplex and trim reads by barcode"
    )
    parser.add_argument("fastq", help="barcoded fastq sequence data")
    parser.add_argument("samples", help="tab-delimited sample file")
    parser.add_argument("reference", help="fasta reference")
    parser.add_argument(
        "--fastqs-dir",
        dest="fastqs_dir",
        help="output fastq folder",
        default=FASTQS_DEFAULT,
    )
    parser.add_argument(
        "--bams-dir", dest="bams_dir", help="output bam folder", default=BAMS_DEFAULT
    )
    parser.add_argument("--report", help="output fastq folder", default=REPORT_DEFAULT)
    parser.add_argument(
        "--reindex", action="store_true", help="force re-indexing of reference"
    )
    parser.add_argument("--force", action="store_true", help="overwrite outputs")
    parser.add_argument(
        "--savesam", action="store_true", help="save intermediate SAM (debugging)"
    )
    args = parser.parse_args()

    # echo inputs
    print(f"sequencing fastq: {args.fastq}")
    print(f"sample file: {args.samples}")
    print(f"reference fasta: {args.reference}")
    print(f"fastqs dir: {args.fastqs_dir}")
    print(f"bams dir: {args.bams_dir}")
    print(f"report file: {args.report}")
    print(f"re-index reference: {args.reindex}")
    print(f"force: {args.force}")
    print(f"save intermdiate SAM: {args.savesam}")

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
                print(
                    f"{output} already exists.  Use --force to overwrite.  Exiting..."
                )
                sys.exit(1)
            else:
                print(f"Deleting existing {output} ...")
                if os.path.isdir(output):
                    _rm_tree(output)
                else:
                    pathlib.Path(output).unlink()

    return args


def verify_prerequisites() -> None:
    """Verify required third-party applications are present"""
    for app in ["bwa", "samtools"]:
        cmd = ["which", app]
        _run_subprocess(cmd, None)


def create_fastqs(samples: SampleFile, fastq_file: str, fastqs_dir: str) -> None:
    """demultplex a fastq by barcode; trim barcodes and low-quality bases
       (1st occurrence of consecutive D/F quality scores)
       and write the new per-barcode fastqs named <name>_trimmed.fastq
       to the output folder. (name = Name field from sample file)

       - Assumes barcodes are of the same length - will raise an exception otherwise
       - Assumes barcodes start at the beginning of the read
       - Skips barcodes with no assigned name

    Args:
        samples (SampleFile): object representation of sample file
        fastq_file (str): fastqs input sequence data
        fastqs_dir (str): output folder of fastqs
    """

    # setup
    regex = re.compile(r"[DF]{2}")  # low quality

    # fastq iterator setup
    SEQHEADER = 0
    SEQ = 1
    QUALHEADER = 2
    QUAL = 3

    fastq_parser = ParseFastQ(fastq_file)
    os.makedirs(fastqs_dir)

    # parse sequence data one read at a time
    for read in fastq_parser:
        # get the barcode
        bc = read[SEQ][: samples.bc_length]
        name = samples.bc_name.get(bc)
        if name:
            # find starting point for trimming low-quality bases
            match = regex.search(read[QUAL])
            end_pos = match.start() if match else None

            # trim
            seq_str = (
                read[SEQ][samples.bc_length : end_pos]
                if end_pos
                else read[SEQ][samples.bc_length :]
            )
            qual_str = (
                read[QUAL][samples.bc_length : end_pos]
                if end_pos
                else read[QUAL][samples.bc_length :]
            )

            # write read - append to existing
            # seems like a lot of I/O - might be a better way to do this
            filename = os.path.join(fastqs_dir, f"{name}{TRIMMED_FASTQ}")
            with open(filename, "a+") as f:
                for read_line in (read[SEQHEADER], seq_str, read[QUALHEADER], qual_str):
                    f.write(f"{read_line}\n")
        else:
            print(f"barcode {bc} has no assigned sample ... skipping")


def align_reads(reference: str, fastqs_dir: str, bams_dir: str, reindex=False) -> None:
    """aligns reads for each fastq and generate a SAM file

        - if index file fa.amb exists, assume the index is already generated

    Args:
        reference (str): reference fasta
        fastqs_dir (str): input trimmed fastqs (filename convention: name_trimmed.fastq)
        bams_dir (str): output folder (filename convention: name.sam)
        reindex (bool): force reference re-index (default False)
    """

    # setup
    os.makedirs(bams_dir)

    # index reference (if needed)
    if not os.path.exists(reference + ".amb") or reindex:
        print("generate index...")
        cmd = ["bwa", "index", reference]
        _run_subprocess(cmd, None)

    # call bwa mem on every trimmed fastq - write to a SAM file
    for fastq_filename in [
        f for f in os.listdir(fastqs_dir) if f.endswith(TRIMMED_FASTQ)
    ]:
        name = fastq_filename.split("_")[0]
        cmd = ["bwa", "mem", reference, os.path.join(fastqs_dir, fastq_filename)]
        samfile = os.path.join(bams_dir, f"{name}.sam")
        with open(samfile, "w") as f:
            _run_subprocess(cmd, f)


def sam_to_bam(bams_dir: str, savesam=False) -> None:
    """Convert sam files to sorted, indexed bam files

    Takes a directory of sam files
    For each sam file
    (1) converts to bam file and deletes the sam file
    (2) sorts and indexes the bam file and deletes the unsorted bam file

    Deletion occurs immediately to minimize disk usage.

    Args:
        bams_dir (str): working directory of sam/bam files
        savesam (bool): do not delete intermediate SAM file (Defaults to False).
    """
    for sam_filename in [f for f in os.listdir(bams_dir) if f.endswith(".sam")]:
        # get filenames
        name = os.path.splitext(sam_filename)[0]
        samfile = os.path.join(bams_dir, sam_filename)
        bamfile = os.path.join(bams_dir, f"{name}.bam")
        sorted_bamfile = os.path.join(bams_dir, f"{name}{SORTED_BAM}")

        # SAM to BAM
        cmd = ["samtools", "view", "-bS", samfile]
        with open(bamfile, "w") as f:
            _run_subprocess(cmd, f)
        if not savesam:
            pathlib.Path(samfile).unlink()

        # sort BAM
        cmd = ["samtools", "sort", "-m", "100M", "-o", sorted_bamfile, bamfile]
        _run_subprocess(cmd, None)
        pathlib.Path(bamfile).unlink()

        # index BAM
        cmd = ["samtools", "index", sorted_bamfile]
        _run_subprocess(cmd, None)


def call_variants(bams_dir: str, reference: str) -> dict:
    """Reports bases for each bam where there is more than 1 base at a position

    Args:
        bams_dir (str): bam file directory (name_sorted.bam)
        reference (str): reference fasta path

    One could in principle get the wildtype from the bam file MD tag
    which would mitigate the need to read the reference

    Returns:
        dict: dictionary of {name: list of VariantFrequency tuples}
    """

    def _get_mutation_base(wildtype: str, frequencies: tuple) -> str:
        """Inner function to get a mutation from a tuple of frequencies

        Assumes exactly one mutation base

        Args:
            wildtype (str): wildtype base
            frequencies (tuple): (base, frequency)

        Returns:
            str: mutation
        """
        mutation = None
        for (base, frequency) in frequencies:
            if base != wildtype and frequency > 0:
                mutation = base
                break
        assert mutation is not None  # you must have one mutation
        return mutation

    # get the reference (for wildtype data)
    with open(reference) as f:
        f.readline()  # skip header
        reference_sequence = f.readline().strip()

    sample_variants = {}
    for bam_filename in [f for f in os.listdir(bams_dir) if f.endswith(SORTED_BAM)]:
        print(f"Processing {bam_filename}...")
        bamfile = os.path.join(bams_dir, bam_filename)
        name = bam_filename.split("_")[0]
        # run the pileup method to get position/# reads/frequencies
        bam_variants = pileup(bamfile)

        # convert each variant into a NamedTuple (add wildtype & mutation)
        if bam_variants:
            variants_complete = []
            for (position, nreads, frequencies) in bam_variants:
                wildtype = reference_sequence[position]
                mutation = _get_mutation_base(wildtype, frequencies)
                # increment position by one since pysam pileups and python lists are 0-based
                variants_complete.append(
                    VariantFrequency(
                        position=position + 1,
                        nreads=nreads,
                        wildtype=wildtype,
                        mutation=mutation,
                        frequencies=frequencies,
                    )
                )
            sample_variants[name] = variants_complete

    return sample_variants


def generate_report(variants: dict, samples: SampleFile, report_file: str) -> None:
    """Generate variants report

    - Iterates through all variants by color, and reports each variant.
    - Iterates through all samples, and reports each variant.

    Code does not assume only 1 variant per color or sample
    (although the reporting text would be admittedly odd in that case)

    Args:
        variants (dict): dictionary of {name:list[VariantCalls]}
        samples (SampleFile): sample object
        report_file (str): path to write report
    """
    # write the report
    with open(report_file, "w") as f:

        # get all the variants for a color
        for color, names in samples.color_names.items():
            color_variants = []
            for name in names:
                color_variants.extend(variants.get(name, []))

            unique_variants = []
            for color_variant in color_variants:
                variant_tuple = (
                    color_variant.position,
                    color_variant.wildtype,
                    color_variant.mutation,
                )
                if variant_tuple not in unique_variants:
                    unique_variants.append(variant_tuple)

            for (position, wildtype, mutation) in unique_variants:
                msg = f"The {color} mold was caused by a mutation in position {position}.  The wildtype base was {wildtype} and the mutation was {mutation}\n"
                f.write(msg)

        f.write("\n")

        # report all the per-sample results
        for name in samples.name_color.keys():
            color = samples.name_color[name]
            for variant in variants.get(name, []):
                for base, frequency in variant.frequencies:
                    if base == variant.mutation:
                        mutation_frequency = frequency
                        break
                msg = f"Sample {name} had a {color} mold, {variant.nreads} reads, and had {mutation_frequency:.0%} of the reads at position {variant.position} had the mutation {variant.mutation}\n"
                f.write(msg)


#
# helper code
#


def _rm_tree(pth):
    """delete a directory and all contents
    https://stackoverflow.com/questions/50186904/pathlib-recursively-remove-directory

    using python 3 pathlib instead of shutil

    Args:
        pth (str): path to a directory
    """
    pth = pathlib.Path(pth)
    for child in pth.glob("*"):
        if child.is_file():
            child.unlink()
        else:
            _rm_tree(child)
    pth.rmdir()


def _run_subprocess(cmd, stdout=None):
    """run a subprocess; exits on failure

    Require a list of strings to avoid using shell=True
    for security reasons

    Args:
        cmd (list): command as a list of strings
        stdout (file, optional): file-type object. Defaults to None.
    """
    cmdstring = " ".join(cmd)
    print(f"running {cmdstring}...")
    try:
        subprocess.run(cmd, check=True, stdout=stdout)
    except subprocess.CalledProcessError as err:
        print(f"{cmdstring} failed: {str(err)}")
        sys.exit(err.returncode)


#
# main
#


def main():
    """main"""
    print("-- Verify prerequisites --")
    args = verify_prerequisites()
    print("-- Parse and validate input --")
    args = parse_arguments()
    print("-- Parse sample file --")
    samples = SampleFile(args.samples)
    print("-- Create demultiplexed trimmed fastqs --")
    create_fastqs(samples, args.fastq, args.fastqs_dir)
    print("-- Align reads --")
    align_reads(args.reference, args.fastqs_dir, args.bams_dir, reindex=args.reindex)
    print("-- Create sorted indexed bam files --")
    sam_to_bam(args.bams_dir, savesam=args.savesam)
    print("-- Call variants --")
    variants = call_variants(args.bams_dir, args.reference)
    print("-- Generate report --")
    generate_report(variants, samples, args.report)


if __name__ == "__main__":
    main()
