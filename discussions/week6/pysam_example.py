#!/usr/bin/env python3

import pysam

TESTFILE = 'test.bam'

def main():

    bamfile = pysam.AlignmentFile(TESTFILE, 'rb')
    for k,v in bamfile.header.items():
        print(k, v)
    for read in bamfile.fetch():
        print(read.cigarstring)

if __name__ == "__main__":
    main()
