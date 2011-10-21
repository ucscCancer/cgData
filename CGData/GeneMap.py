#!/usr/bin/env python

import csv
import sys
import re


class ProbeMapper:
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
