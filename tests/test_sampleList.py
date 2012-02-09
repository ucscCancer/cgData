#!/usr/bin/env python

import unittest
import os
import sys
import CGData
import CGData.IDList

class TestCase(unittest.TestCase):
    def test_segmap_simple(self):
        idList = CGData.load("data_sampleList2/tcga.samplelist")        
        assert len(idList.get_key_list()) == 20
        
        matrix = CGData.load("data_sampleList2/tcga.matrix")
        assert matrix.get_shape() == (2,20)
        
        iddag = CGData.load("data_sampleList2/tcga.iddag")
        
        wl = CGData.IDList.WhiteLister(idList, iddag)
        
        out = wl.whitelist_matrix(matrix)
        assert out.get_shape() == (2,20)
        

def main():
    sys.argv = sys.argv[:1]
    unittest.main()

if __name__ == '__main__':
    main()
