#!/usr/bin/env python

import csv
import sys
import re

import CGData.GenomicMatrix

class ProbeMapper(object):
    """
    Class to map the probes. Expects handle to the refGene_hg18.table file
    """

    def __init__(self, mode='g'):
        self.cmp_func = optionMap[mode]

    def find_overlap(self, segment, ref_gene, cmp_func=None):
        """
        Function to find overlaps for a given probe description.
        the cmp_func arg is a function that returns a 'True' or 'False' for
        a given probe description and a gene, examples include 'gene_overlap'
        and 'gene_simple_meth_overlap'
        """
        if cmp_func is None:
            cmp_func = self.cmp_func
        if not ref_gene.has_chrom(segment.chrom):
            return []
        chromList = ref_gene.get_chrom(segment.chrom)

        out = []
        for gene in chromList:
            if cmp_func(segment.chrom_start,
                        segment.chrom_end, segment.strand, gene):
                out.append(gene)
        return out


#
# The set of functions that can be used to do comparisons
#


def gene_overlap(start, end, strand, gene):
    if ((gene.strand == strand or strand == '.' or gene.strand == '.')
    and gene.chrom_end > start
    and gene.chrom_start < end):
        return True
    return False


def block_overlap(start, end, strand, gene):
    if gene.chrom_end > start and gene.chrom_start < end:
        return True
    return False


def exon_overlap(start, end, strand, gene):
    if gene.strand != strand and gene.strand != '.' and strand != '.':
        return False
    for i in range(int(gene.ex_count)):
        if gene.ex_end[i] > start and gene.ex_start[i] < end:
            return True
    return False


def gene_simple_meth_overlap(start, end, strand, gene):
    if gene.chrom_end > start and gene.chrom_start < end:
        return True
    return False

###ADD MORE FUNCTIONS HERE


####

###To add options to the command line, map the option character to a function
###for example '-m' maps to gene_simple_meth_overlap

optionMap = {
    "g": gene_overlap,
    "b": block_overlap,
    "m": gene_simple_meth_overlap,
    "e": exon_overlap,
}



def genomicSegment2Matrix(genomicSegment, refGene, probeMapper):
    """
    Take a genomicSegment map, compare it against a refGene table,
    and contruct a genomicMatrix
    """
    out = CGData.GenomicMatrix.GenomicMatrix()
    out.init_blank( rows=refGene.get_gene_list(), cols=genomicSegment.get_id_list() )
    for id in genomicSegment.get_id_list():
        for segment in genomicSegment.get_by_id(id):
            for hit in probeMapper.find_overlap( segment, refGene ):
                out.set_val(row_name=hit.name, col_name=segment.id, value=segment.value )
    return out


def filter_longest_form(refgene):
    """
    take a refgene table and filter multiple gene isoforms down to the longest
    """
    ng = CGData.RefGene.RefGene()
    for g in refgene.get_gene_list():
        longest = None
        length = 0
        for elem in refgene.get_gene(g):
            newLength = elem.chrom_end - elem.chrom_start
            if newLength > length:
                length = newLength
                longest = elem
        ng.add(longest)
    return ng


def genomicSegment2MatrixNorm(genomicSegment, refGene, probeMapper):
    ng = filter_longest_form(refGene)
    #enumerate the col order of the sample ids
    idList = genomicSegment.get_id_list()
    
    geneList = ng.get_gene_list()
    
    out = CGData.GenomicMatrix.GenomicMatrix()
    out.init_blank( rows=geneList, cols=idList )
    
    #read through the segment one sample id at a time
    for id in idList:   
        segmentMap = {}
        for segment in genomicSegment.get_by_id(id):
            for hit in probeMapper.find_overlap( segment, ng ):
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
            out.set_val(row_name=gene, col_name=id, value=value/coverage)

    return out
