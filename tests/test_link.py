#!/usr/bin/env python

import unittest
import os

import CGData
import CGData.DataSet

CGData.LOG_LEVEL=0
class TestCase(unittest.TestCase):
    def test_load(self):
        
        ds = CGData.DataSet.DataSet()
        ds.scan_dirs( ["data_link2/"] )
        
        fileTypes = ds.get_file_types()
        assert "genomicMatrix" in fileTypes
        assert "clinicalMatrix" in fileTypes
        
        mapTypes = ds.get_map_types()
        print mapTypes
        assert "probe" in mapTypes
        
        print ds['genomicMatrix']['test'].get_link_map()
        
        ms = ds.query(src_type='id', dst_type='genomicMatrix')
        assert ms[0]['name'] == "test"
        
        ms = ds.query(src_type='id', predicate='rowKeyMap')
        assert ms[0]['name'] == "test"

        fs = ds.query(src_type='genomicMatrix', src_name='test', dst_type='id')
        assert fs[0]['name'] == "test"
        


def main():
    sys.argv = sys.argv[:1]
    unittest.main()

if __name__ == '__main__':
    main()
