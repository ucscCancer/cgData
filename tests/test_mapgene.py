#!/usr/bin/env python

import unittest
import os
import sys
import CGData
import CGData.GeneMap

class TestCase(unittest.TestCase):
    def test_segmap_simple(self):
        sg = CGData.load("data_mapgenes2/test.genomicSegment")
        rg = CGData.load("data_mapgenes2/test.refgene")
        pm = CGData.GeneMap.ProbeMapper('b')

        out = CGData.GeneMap.genomicSegment2Matrix(sg,rg,pm)
        assert out.get_shape() == (21,1)

        
    def test_segmap_norm(self):
        sg = CGData.load("data_mapgenes2/test.genomicSegment")
        rg = CGData.load("data_mapgenes2/test.refgene")
        pm = CGData.GeneMap.ProbeMapper('b')

        out = CGData.GeneMap.genomicSegment2MatrixNorm(sg,rg,pm)
        assert out.get_shape() == (10,1)

    def test_aliasmap(self):
        mt = CGData.load("data_mapgenes2/test.genomicMatrix")
        am = CGData.load("data_mapgenes2/test.probeMap.aliasmap")
        
        out = CGData.GeneMap.aliasRemap(mt, am)
        assert out.get_shape() == (9,81)

def main():
    sys.argv = sys.argv[:1]
    unittest.main()

if __name__ == '__main__':
    main()
