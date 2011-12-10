#!/usr/bin/env python

import unittest
import os

import CGData

class TestCase(unittest.TestCase):
    def test_load(self):
        m = CGData.load("data_basic/probeMap_test")
        print m.get_probe_list()
        

def main():
    sys.argv = sys.argv[:1]
    unittest.main()

if __name__ == '__main__':
    main()
