#!/usr/bin/env python

import sys
import csv

import CGData.GenomicSegment
import CGData.GeneMap
import CGData.RefGene
import CGData.GenomicMatrix
import numpy

handle = open( sys.argv[1] )
sg = CGData.GenomicSegment.GenomicSegment()
sg.read( handle )
sg.loaded = True
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


#enumerate the col order of the sample ids
idList = {}
for num, id in enumerate(sg.get_id_list()):
    idList[id] = num


geneList = {}
for num, id in enumerate(ng.get_gene_list()):
    geneList[id] = num

out = numpy.empty((len(geneList),len(idList)))
out.fill(numpy.nan)

#read through the segment one sample id at a time
for id in idList:   
    print id
    segmentMap = {}
    for segment in sg.get_by_id(id):
        for hit in pm.find_overlap( segment, ng ):
            span = float(min(segment.chrom_end, hit.chrom_end) - max(segment.chrom_start, hit.chrom_start)) / float(hit.chrom_end - hit.chrom_start)
            #if hit.name not in segmentMap:
            #    segmentMap[hit.name] = []
            try:
                segmentMap[hit.name].append(
                    ( span, segment.value )
                )
            except KeyError:
                segmentMap[hit.name] = [
                    ( span, segment.value )
                ]
    
    for gene in segmentMap:
        mapInfo = segmentMap[gene]
        coverage = sum( i[0] for i in mapInfo )
        assert coverage <= 1.0
        value = sum( i[0]*i[1] for i in mapInfo )
        #print coverage, value, value/coverage, segmentMap[gene]
        out[geneList[gene]][idList[id]] = value/coverage
    #print id
    
handle = open(sys.argv[3], "w")
writer = csv.writer(handle, delimiter="\t", lineterminator="\n")

row = ["NA"] * len(idList)
for id in idList:
    row[ idList[id] ] = id
writer.writerow( ["probe"] + row )

for gene in geneList:
    row = ["NA"] * (len(idList))
    found = False
    geneRow = out[geneList[gene]]
    for j,val in enumerate(geneRow):
        if val != numpy.nan:
            row[j] = str(val)
            found = True
    writer.writerow( [gene] + row )
        
#for segment in out:
#   print segment, out[segment]
