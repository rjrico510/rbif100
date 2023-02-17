#!/usr/bin/env python3

import pybedtools

TESTFILE='tiny.bed'

def main():
    bedfile = pybedtools.BedTool(TESTFILE)
    interval = pybedtools.cbedtools.create_interval_from_list(['chr1', '100', '200'])
    all_hits = bedfile.all_hits(interval)
    print(all_hits)

if __name__ == '__main__':
    main()
