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
        
        print ds['genomicMatrix']['test.genomicMatrix'].get_link_map()
        
        ms = ds.find_map_links('id', None, None, 'genomicMatrix', None)
        assert ms[0]['name'] == "test.genomicMatrix"
        
        ms = ds.find_map_links('id', None, 'rowKeyMap', None, None)
        assert ms[0]['name'] == "test.clinicalMatrix"

        fs = ds.find_file_links('genomicMatrix', 'test.genomicMatrix', None, 'id', None)
        assert fs[0]['name'] == "test.sampleMap"
        


def main():
    sys.argv = sys.argv[:1]
    unittest.main()

if __name__ == '__main__':
    main()
