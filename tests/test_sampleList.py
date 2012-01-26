#!/usr/bin/env python

import unittest
import os
import sys
import CGData
import CGData.GeneMap

class TestCase(unittest.TestCase):
    def test_segmap_simple(self):
        idList = CGData.load("data_sampleList2/tcga.samplelist")        
        
        assert len(idList.get_id_list()) == 20

def main():
    sys.argv = sys.argv[:1]
    unittest.main()

if __name__ == '__main__':
    main()
