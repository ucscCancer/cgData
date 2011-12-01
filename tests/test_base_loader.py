#!/usr/bin/env python

import unittest
import os

import CGData.Base

class TestCase(unittest.TestCase):
    def test_load(self):
        m = CGData.Base.load("data_basic/probeMap_test")
        print m.get_probeName_list()
        

def main():
    sys.argv = sys.argv[:1]
    unittest.main()

if __name__ == '__main__':
    main()
