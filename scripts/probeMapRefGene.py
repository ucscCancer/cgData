#!/usr/bin/env python
"""

This script take a cgData2 probeMap file, and maps it aginst a refGene
file, producing an aliasMap file

Usage: probeMapRefGene.py [options] probeMapFile refGeneFile

Options:
  -h, --help            show this help message and exit
  -d DATASUBTYPE, --datasub-type=DATASUBTYPE
                        DatasubType : (DNAMethylation, PARADIGM.pathlette,
                        geneExp, RPPA, SNP, cna, PARADIGM)
  -1, --cgdata-v1       output cgdata v1 probemap
  -o OUTPUT, --output=OUTPUT
                        Output File

"""
import sys
import csv

from optparse import OptionParser

import CGData.ProbeMap
import CGData.GeneMap
import CGData.RefGene


dataSubTypeMap = {
    'geneExp' : 'e',
    'cna' : 'b',
    'PARADIGM': 'e',
    'DNAMethylation' : 'm',
    'PARADIGM.pathlette' : 'e',
    'RPPA' : 'b',
    'SNP' : 'b'
}

if __name__ == "__main__":
    usage = "usage: %prog [options] <probeMapFile> <refGeneFile>"
    parser = OptionParser(usage=usage)
    parser.add_option("-d", "--datasub-type", dest="dataSubType", help="DatasubType : (%s)" % (", ".join(dataSubTypeMap.keys())) , default="geneExp")
    parser.add_option("-1", "--cgdata-v1", dest="version1", action="store_true", help="output cgdata v1 probemap", default=False)
    parser.add_option("-o", "--output", dest="output", help="Output File", default="out")
    options, args = parser.parse_args()

    handle = open( args[0] )
    pm = CGData.ProbeMap.ProbeMap()
    pm.read( handle )
    pm.loaded = True
    handle.close()

    handle = open( args[1] )
    rg = CGData.RefGene.RefGene()
    rg.read( handle )
    handle.close()
    
    mapper = CGData.GeneMap.ProbeMapper(dataSubTypeMap[options.dataSubType])
    
    for probeName in pm.get_probe_list():
        hits = {}
        probe = pm.get_by_probe(probeName)
        for hit in mapper.find_overlap(probe, rg):
            hits[hit.name] = True
        
        if options.version1:
            print "%s\t%s\t%s\t%s\t%s" % (probeName, ",".join(hits.keys()), probe.chrom_start, probe.chrom_end, probe.strand)                
        else:
            for hit in hits:
                print "%s\t%s" % (probeName, hit)
    
    #out = CGData.GeneMap.genomicSegment2MatrixNorm(sg,rg,pm)
    #out.save(options.out)

