#!/usr/bin/env python

import sys

import CGData.GenomicSegment
import CGData.GeneMap
import CGData.RefGene
import CGData.GenomicMatrix
import numpy

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

#filter multiple gene isoforms down to the longest
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

geneHash = {}
out = {}

#enumerate the col order of the sample ids
idList = {}
for num, id in enumerate(sg.get_id_list()):
    idList[id] = num

#read through the segment one sample id at a time
for id in idList:   
    print id
    segmentMap = {}
    for segment in sg.get_id(id):
        for hit in pm.find_overlap( segment, ng ):
            if hit.name not in segmentMap:
                segmentMap[hit.name] = []
        
            if hit.name not in geneHash:
                geneHash[hit.name] = len(geneHash)
            
            span = float(min(segment.chrom_end, hit.chrom_end) - max(segment.chrom_start, hit.chrom_start)) / float(hit.chrom_end - hit.chrom_start)
        
            segmentMap[hit.name].append(
                ( span, segment.value )
            )

    o = numpy.empty(len(geneHash))  
    o.fill(numpy.nan)
    for gene in segmentMap:
        mapInfo = segmentMap[gene]
        coverage = sum( i[0] for i in mapInfo )
        assert coverage <= 1.0
        value = sum( i[0]*i[1] for i in mapInfo )
        #print coverage, value, value/coverage, segmentMap[gene]
        o[geneHash[gene]] = value/coverage
    out[id] = o
    #print id


for gene in geneHash:
    row = ["NA"]
    for id in idList:
        if len(out[id]) > geneHash[gene]:
            row[idList[id]] = out[id][geneHash[gene]]
    print row
        
#for segment in out:
#   print segment, out[segment]
