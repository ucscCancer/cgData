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

out = {}


def filter_longest_form(refgene):
	ng = CGData.RefGene.RefGene()
	for g in rg.get_gene_list():
		longest = None
		length = 0
		for elem in rg.get_gene(g):
			newLength = elem.chrom_end - elem.chrom_start
			if newLength > length:
				length = newLength
				longest = elem
		ng.add(longest)
	return ng

ng = filter_longest_form(rg)

out = {}
for segment in sg.get_segments():	
	if segment.sample not in out:
		out[ segment.sample ] = {}
	segmentMap = out[segment.sample]
	for hit in pm.find_overlap( segment, ng ):
		if hit.name not in segmentMap:
			segmentMap[hit.name] = []
		
		span = float(min(segment.chrom_end, hit.chrom_end) - max(segment.chrom_start, hit.chrom_start)) / float(hit.chrom_end - hit.chrom_start)
		
		#segmentMap[hit.name].append(
		#	( span, segment.value )
		#)

for segment in out:
	print segment, out[segment]
