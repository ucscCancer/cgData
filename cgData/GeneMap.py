#!/usr/bin/env python

import csv
import sys
import re


class ProbeMapper:
    """
    Class to map the probes. Expects handle to the refGene_hg18.table file
    """

    def __init__(self, mode='g'):
        self.cmpFunc = optionMap[mode]

    def findOverlap(self, segment, refGene, cmpFunc=None):
        """
        Function to find overlaps for a given probe description.
        the cmpFunc arg is a function that returns a 'True' or 'False' for
        a given probe description and a gene, examples include 'geneOverlap'
        and 'geneSimpleMethOverlap'
        """
        if cmpFunc is None:
            cmpFunc = self.cmpFunc
        if not refGene.hasChrom(segment.chrom):
            return []
        chromList = refGene.getChrom(segment.chrom)

        out = []
        for gene in chromList:
            if cmpFunc(segment.chromStart,
            segment.chromEnd, segment.strand, gene):
                out.append(gene)
        return out


#
# The set of functions that can be used to do comparisons
#


def geneOverlap(start, end, strand, gene):
    if gene.strand == gene.strand\
    and gene.chromEnd > start\
    and gene.chromStart < end:
        return True
    return False


def blockOverlap(start, end, strand, gene):
    if gene.chromEnd > start and gene.chromStart < end:
        return True
    return False


def exonOverlap(start, end, strand, gene):
    if gene.strand != gene.strand:
        return False
    for i in range(gene.exCount):
        if gene.exEnd[i] > start and gene.exStart[i] < end:
            return True
    return False


def geneSimpleMethOverlap(start, end, strand, gene):
    if gene.chromEnd > start and gene.chromStart < end:
        return True
    return False

###ADD MORE FUNCTIONS HERE


####

###To add options to the command line, map the option character to a function
###for example '-m' maps to geneSimpleMethOverlap

optionMap = {
    "g": geneOverlap,
    "b": blockOverlap,
    "m": geneSimpleMethOverlap,
    "e": exonOverlap,
}
