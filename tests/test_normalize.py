#!/usr/bin/env python

import unittest
import os
import sys
import CGData
import CGData.Normalize

class TestCase(unittest.TestCase):
    def test_median_normalize(self):
        mt = CGData.load("data_mapgenes2/test.genomicMatrix")       
        out = CGData.Normalize.row_median_shift(mt)
        assert abs( out.get_val(row_name="cg00000292", col_name="TCGA-07-0227-20A-01D-0820-05") - -0.302657466678 ) < 0.000001

    def test_norm_normalize(self):
        norm_list = [ 
            "TCGA-AF-2689-11A-01D-1552-05", 
            "TCGA-AF-2691-11A-01D-1552-05", 
            "TCGA-AF-2692-11A-01D-1552-05",
            "TCGA-AF-3400-11A-01D-1552-05",
            "TCGA-AF-3913-11A-01D-1116-05" 
        ]
        mt = CGData.load("data_mapgenes2/test.genomicMatrix")
        out = CGData.Normalize.norm_row_median_shift(mt, norm_list)
        assert abs( out.get_val(row_name="cg00000292", col_name="TCGA-07-0227-20A-01D-0820-05") - -0.2397101 ) < 0.000001

def main():
    sys.argv = sys.argv[:1]
    unittest.main()

if __name__ == '__main__':
    main()
