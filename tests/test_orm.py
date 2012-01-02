#!/usr/bin/env python

import unittest
import os

import CGData
import CGData.ORM
import CGData.DataSet

class TestCase(unittest.TestCase):
    def test_load(self):
        
        if os.path.exists("test.orm.sqlite"):
                os.unlink( "testfile.orm.sqlite" )
        if os.path.exists("testfile.orm.hdf5"):
                os.unlink( "testfile.orm.hdf5" )
            
        ds = CGData.DataSet.DataSet()
        ds.scan_dirs( ["data_basic2/"] )
        
        orm = CGData.ORM.ORM("testfile.orm")        
        orm.add_all(ds)
        orm.close()
        


def main():
    sys.argv = sys.argv[:1]
    unittest.main()

if __name__ == '__main__':
    main()
