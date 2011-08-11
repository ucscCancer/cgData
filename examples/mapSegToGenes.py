#!/usr/bin/env python

import sys

import cgData.genomicSegment
import cgData.geneMap
import cgData.refGene
import cgData.geneMap 
import cgData.matrix

handle = open( sys.argv[1] )
sg = cgData.genomicSegment.genomicSegment()
sg.read( handle )
handle.close()

handle = open( sys.argv[2] )
rg = cgData.refGene.refGene()
rg.read( handle )
handle.close()

pm = cgData.geneMap.ProbeMapper('b')

out = cgData.matrix.GeneMatrix()

for sample in sg:
    sys.stderr.write( sample + "\n" )
    for seg in sg[sample]:
        for hit in pm.findOverlap( seg, rg ):
            out.add( probe=hit, sample=sample, value=seg.value )

out.write( sys.stdout )     
