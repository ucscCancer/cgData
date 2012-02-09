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
    'geneExp' : { 'same_strand' : True, 'exons' : True },
    'cna' : { 'same_strand' : False, 'exons' : False },
    'PARADIGM':  { 'same_strand' : True, 'exons' : True },
    'DNAMethylation' :  { 'same_strand' : False, 'exons' : False},
    'PARADIGM.pathlette' : { 'same_strand' : True, 'exons' : True },
    'RPPA' : { 'same_strand' : True, 'exons' : True },
    'SNP' : { 'same_strand' : False, 'exons' : True },
    'siRNAViability' : { 'same_strand' : True, 'exons' : True }
}

if __name__ == "__main__":
    usage = "usage: %prog [options] <probeMapFile> <refGeneFile>"
    parser = OptionParser(usage=usage)
    parser.add_option("-d", "--dataSubType", dest="dataSubType", help="DatasubType : (%s)" % (", ".join(dataSubTypeMap.keys())) , default="geneExp")
    parser.add_option("-1", "--cgdata-v1", dest="version1", action="store_true", help="output cgdata v1 probemap", default=False)
    parser.add_option("-n", "--minCoverage", dest="coverage", type="float", help="Min coverage", default=None)
    parser.add_option("-o", "--output", dest="output", help="Output File", default="out")
    parser.add_option("--start_rel_tss", dest="start_rel_tss", type="int", default=None)
    parser.add_option("--end_rel_tss", dest="end_rel_tss", type="int", default=None)
    parser.add_option("--start_rel_cdsStart", dest="start_rel_cdsStart", type="int", default=None)
    parser.add_option("--end_rel_cdsStart", dest="end_rel_cdsStart", type="int", default=None)
    
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
    
    mapper = CGData.GeneMap.ProbeMapper()
    
    conf = dataSubTypeMap[ options.dataSubType ]
    for a in [ 'coverage', 'start_rel_tss', 'end_rel_tss', 'start_rel_cdsStart', 'end_rel_cdsStart' ]:
        if getattr(options, a) is not None:
            conf[a] = getattr(options, a)
    intersector = CGData.GeneMap.Intersector( **conf )
    
    ohandle = open(options.output, "w")    
    for probeName in pm.get_key_list():
        hits = {}
        probe = pm.get_by(probeName)
        for hit in mapper.find_overlap(probe, rg, intersector.hit):
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
    
    
