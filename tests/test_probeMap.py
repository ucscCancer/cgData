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

    def test_GeneExp_array_probe(self):
        subprocess.check_call( "../scripts/probeMapRefGene.py --dataSubType=geneExp --minCoverage=75 --output=outputFile data_mapgenes2/test.probeMap data_mapgenes2/test.refgene", shell=True )
    
    def test_GeneExp_HUGO_probe(self):
        subprocess.check_call( "../scripts/probeMapRefGene.py  --dataSubType=geneExp --minCoverage=75 --output=outputFile data_mapgenes2/test.probeMap data_mapgenes2/test.refgene", shell=True )

    def test_siRNA_data_in_HUGO_probe(self):
        subprocess.check_call( "../scripts/probeMapRefGene.py  --dataSubType=siRNAViability --minCoverage=75 --output=outputFile data_mapgenes2/test.probeMap data_mapgenes2/test.refgene", shell=True )

    def test_PARADIGM_data_in_HUGO_probe(self):
        subprocess.check_call( "../scripts/probeMapRefGene.py  --dataSubType=PARADIGM --minCoverage=75 --output=outputFile data_mapgenes2/test.probeMap data_mapgenes2/test.refgene", shell=True )

    def test_PARADIGMLite_data_in_HUGO_probe(self):
        subprocess.check_call( "../scripts/probeMapRefGene.py  --dataSubType=PARADIGM.pathlette --minCoverage=75 --output=outputFile data_mapgenes2/test.probeMap data_mapgenes2/test.refgene", shell=True )

    def test_cna_array_probe(self):
        subprocess.check_call( "../scripts/probeMapRefGene.py  --dataSubType=cna --minCoverage=75 --output=outputFile data_mapgenes2/test.probeMap data_mapgenes2/test.refgene", shell=True )

    def test_cna_segments(self):
        subprocess.check_call( "../scripts/probeMapRefGene.py  --dataSubType=cna --minCoverage=0 --output=outputFile data_mapgenes2/test.probeMap data_mapgenes2/test.refgene", shell=True )

    def test_DNA_methylation_probes(self):
        subprocess.check_call( "../scripts/probeMapRefGene.py  --dataSubType=DNAMethylation --minCoverage=75 --output=outputFile data_mapgenes2/test.probeMap data_mapgenes2/test.refgene", shell=True )


def main():
    sys.argv = sys.argv[:1]
    unittest.main()

if __name__ == '__main__':
    main()
