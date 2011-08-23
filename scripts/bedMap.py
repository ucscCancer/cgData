#!/usr/bin/env python

import sys
import CGData.GeneMap
import CGData.RefGene
import CGData.Bed
import CGData.ProbeMap

from getopt import getopt
import csv

opts, args = getopt( sys.argv[1:], "".join(CGData.GeneMap.optionMap.keys()) )


#hitFunc is the function that will be used to do the overlap comparision
hitFunc = CGData.GeneMap.gene_overlap
for a, o in opts:
    hitFunc = CGData.GeneMap.optionMap[ a[1:] ]

handle = open( args[0] )
refGene = CGData.RefGene.RefGene( )
refGene.read( handle )

handle.close()
handle = open( args[1] )
bedFile = CGData.Bed.Bed( )
bedFile.read( handle )

mapper = CGData.GeneMap.ProbeMapper( )

for bed in bedFile:
    out = mapper.find_overlap( bed, refGene, hitFunc )
    o = []
    
    bed.aliases = []
    for e in out:
        bed.aliases.append( e.name )
       
    print "%s\t%s" % (bed.name, ",".join(bed.aliases))

