#!/usr/bin/env python

import sys

import CGData.GenomicSegment
import CGData.GeneMap
import CGData.RefGene
import CGData.GenomicMatrix

handle = open( sys.argv[1] )
sg = CGData.GenomicSegment.GenomicSegment()
sg.read( handle )
handle.close()

handle = open( sys.argv[2] )
rg = CGData.RefGene.RefGene()
rg.read( handle )
handle.close()

pm = CGData.GeneMap.ProbeMapper('b')

out = CGData.GenomicMatrix.GenomicMatrix()
out.blank()

for sample in sg:
    sys.stderr.write( sample + "\n" )
    for seg in sg[sample]:
        for hit in pm.find_overlap( seg, rg ):
            out.add( probe=hit, sample=sample, value=seg.value )

out.write( sys.stdout )     
