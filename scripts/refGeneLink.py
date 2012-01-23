#!/usr/bin/env python

import CGData
import sys

if __name__ == "__main__":

    ref=CGData.load(sys.argv[2])

    handle = open(sys.argv[1])
    for line in handle:
        tmp = line.rstrip().split("\t")
        sGene = None
        for geneName in tmp[1].split(','):
            try:
                for gene in ref.get_gene(geneName):
                    if sGene is None or gene.chrom_end - gene.chrom_start > sGene.chrom_end - sGene.chrom_start:
                        sGene = gene
            except KeyError:
                pass
        if sGene is not None:
            print "%s\t%s\t%s\t%s\t%s\t%s" % (tmp[0], sGene.name, sGene.chrom, sGene.chrom_start, sGene.chrom_end, sGene.strand)

