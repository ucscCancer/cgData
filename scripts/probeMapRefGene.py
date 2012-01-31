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
import os
from optparse import OptionParser

import CGData.ProbeMap
import CGData.GeneMap
import CGData.RefGene
import json

dataSubTypeMap = {
    'geneExp' : 'g',
    'cna' : 'b',
    'PARADIGM': 'g',
    'DNAMethylation' : 'b',
    'PARADIGM.pathlette' : 'g',
    'RPPA' : 'g',
    'SNP' : 'b',
    'siRNAViability' : 'g'
}

if __name__ == "__main__":
    usage = "usage: %prog [options] <probeMapFile> <refGeneFile>"
    parser = OptionParser(usage=usage)
    parser.add_option("-d", "--dataSubType", dest="dataSubType", help="DatasubType : (%s)" % (", ".join(dataSubTypeMap.keys())) , default="geneExp")
    parser.add_option("-1", "--cgdata-v1", dest="version1", action="store_true", help="output cgdata v1 probemap", default=False)
    parser.add_option("-n", "--minCoverage", dest="minCoverage", type="float", help="Min coverage", default=0.0)
    parser.add_option("-o", "--output", dest="output", help="Output File", default="out")
    options, args = parser.parse_args()

    pm_meta = {}
    handle = open( args[0] )
    pm = CGData.ProbeMap.ProbeMap()
    pm.read( handle )
    pm.loaded = True
    handle.close()
    
    if os.path.exists( args[0] + ".json" ):
        handle = open( args[0] + ".json" )
        pm_meta = json.loads( handle.read() )
        handle.close()
    else:
        pm_meta = { "cgdata" : { "name" : os.path.basename(args[0])} }

    handle = open( args[1] )
    rg = CGData.RefGene.RefGene()
    rg.read( handle )
    handle.close()
    
    mapper = CGData.GeneMap.ProbeMapper(dataSubTypeMap[options.dataSubType])
    
    ohandle = open(options.output, "w")    
    for probeName in pm.get_probe_list():
        hits = {}
        probe = pm.get_by_probe(probeName)
        for hit in mapper.find_overlap(probe, rg):
            hits[hit.name] = True
        
        if options.version1:
            ohandle.write( "%s\t%s\t%s\t%s\t%s\n" % (probeName, ",".join(hits.keys()), probe.chrom_start, probe.chrom_end, probe.strand) )
        else:
            for hit in hits:
                ohandle.write("%s\t%s\n" % (probeName, hit))
    
    ohandle.close()
    ohandle = open(options.output + ".json", "w")
    
    if options.version1:
        ohandle.write( json.dumps( {"type" : "probeMap", "name" : pm_meta['cgdata']['name']} ) )
    else:
        ohandle.write( json.dumps( { "cgdata" : {"type" : "probeMap", "name" : pm_meta['cgdata']['name']} } ) )        
    ohandle.close()
    
    
