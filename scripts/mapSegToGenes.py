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

for segment in sg.get_segments():
	for hit in pm.find_overlap( segment, rg ):
		out.add(probe=hit, sample=segment.sample, value=segment.value )

out.write( sys.stdout )     
