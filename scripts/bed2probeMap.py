#!/usr/bin/env python

import sys
import cgData.geneMap
import cgData.refGene
import cgData.bed
import cgData.probeMap

from getopt import getopt
import csv

opts, args = getopt( sys.argv[1:], "".join(cgData.geneMap.optionMap.keys()) )


#hitFunc is the function that will be used to do the overlap comparision
hitFunc = cgData.geneMap.geneOverlap
for a, o in opts:
    hitFunc = cgData.geneMap.optionMap[ a[1:] ]

handle = open( args[0] )
refGene = cgData.refGene.refGene( )
refGene.read( handle )

handle.close()
handle = open( args[1] )
bedFile = cgData.bed.bed( )
bedFile.read( handle )

mapper = cgData.geneMap.ProbeMapper( )

pm = cgData.probeMap.probeMap()

for bed in bedFile:
    out = mapper.findOverlap( bed, refGene, hitFunc )
    o = []
    
    bed.aliases = []
    for e in out:
        bed.aliases.append( e.name )

    pm.append( bed )

pm.write( sys.stdout )
