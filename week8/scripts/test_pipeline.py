#!/usr/bin/env python3

import unittest

import pipeline

class TestORF(unittest.TestCase):

    def test_orf_tinyTAA(self):
        input = "ATGTAA"
        expected = "ATGTAA"
        actual = pipeline._get_longest_orf_aa(input)
        self.assertTrue(expected, actual)

    def test_orf_tinyTAG(self):
        input = "ATGTAG"
        expected = "ATGTAG"
        actual = pipeline._get_longest_orf_aa(input)
        self.assertTrue(expected, actual)

    def test_orf_tinyTGA(self):
        input = "ATGTGA"
        expected = "ATGTGA"
        actual = pipeline._get_longest_orf_aa(input)
        self.assertTrue(expected, actual)

    def test_orf_offset(self):
        input = "TTTATGATGAATGAATGATTT"
        expected = "ATGATGAATGAATGA"
        actual = pipeline._get_longest_orf_aa(input)
        self.assertTrue(expected, actual)

    def test_orf_multiple_stops(self):
        input = "TTATGCCCTAATAATT"
        expected = "ATGCCCTAA"
        actual = pipeline._get_longest_orf_aa(input)
        self.assertTrue(expected, actual)

    def test_orf_none(self):
        input = "TTATGATAA"
        actual = pipeline._get_longest_orf_aa(input)
        self.assertIsNone(actual)

    def test_orf_multiple_start(self):
        input = "CCCCCATGCCCATGCTAACCTAACTAACTAACCCCCC"
        expected = "ATGCCCATGCTAACCTAA"
        actual = pipeline._get_longest_orf_aa(input)
        self.assertTrue(expected, actual)

    def test_orf_multiple_matches(self):
        input = "ATGCCCTAACATGAAACCCTTTTGACCATGGGGTAA"
        expected = "ATGAAACCCTTTTGA"
        actual = pipeline._get_longest_orf_aa(input)
        self.assertTrue(expected, actual)

if __name__ == "__main__":
    unittest.main()