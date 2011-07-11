#!/usr/bin/env python


import unittest

import cgData.genomicMatrix

class TestCase(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
    
    def tearDown(self):
        unittest.TestCase.tearDown(self)

             
def main():
    sys.argv = sys.argv[:1]
    unittest.main()

if __name__ == '__main__':
    main()
