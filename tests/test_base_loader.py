#!/usr/bin/env python

import unittest
import os

import CGData

class TestCase(unittest.TestCase):
    def test_load(self):
        m = CGData.load("data_basic2/probeMap_test")
        probes = list( m.get_probe_list() )
        assert probes[0] == "probe1"

    def test_segment(self): 
        m = CGData.load("data_segment2/genomicSegment_test")
        assert len( list( m.get_id_list() ) ) == 1
        for a in m.get_id_values():
            assert len(list(a)) == 10
            for seg in a:
                assert type(seg.chrom_start) == int
                assert type(seg.chrom_end) == int
                assert type(seg.value) == float

        count = 0
        for id in m.get_id_list():   
            for segment in m.get_by_id(id):
                count += 1
        assert count == 10




def main():
    sys.argv = sys.argv[:1]
    unittest.main()

if __name__ == '__main__':
    main()
