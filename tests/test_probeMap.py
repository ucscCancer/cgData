#!/usr/bin/env python

import unittest
import os
import sys
import subprocess
import CGData
import CGData.GeneMap

class TestCase(unittest.TestCase):
    def test_probemap(self):

        subprocess.check_call( "../scripts/probeMapRefGene.py -d cna data_mapgenes2/test.probeMap data_mapgenes2/test.refgene -o test_aliasMap", shell=True )
        
        ##do file checks and assert file contains expected information

def main():
    sys.argv = sys.argv[:1]
    unittest.main()

if __name__ == '__main__':
    main()
