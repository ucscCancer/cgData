
import csv
import re
import CGData

#column definitions for the current refGene_hg18.table
COL_CHROM = 2
COL_STRAND = 3
COL_START = 4
COL_END = 5
COL_EXCOUNT = 8
COL_EXSTART = 9
COL_EXEND = 10
COL_HUGO = 12


#sometimes the ref table ends with a comma, which makes
#arrays that end with '' when you split
re_comma_end = re.compile(r',$')


class GeneInfo:
    """
    Class to hold information about gene, including exon start/stops
    """

    def __init__(self,
    chrom, strand, start, end, ex_count, ex_start, ex_end, hugo):
        self.chrom = chrom
        self.strand = strand
        self.chrom_start = int(start)
        self.chrom_end = int(end)
        self.ex_count = ex_count
        self.ex_start = []
        for p in re_comma_end.sub("", ex_start).split(','):
            self.ex_start.append(int(p))
        self.ex_end = []
        for p in re_comma_end.sub("", ex_end).split(','):
            self.ex_end.append(int(p))
        self.name = hugo

    def __repr__(self):
        #return "%s_%s_%d_%d" % (self.hugo, self.chrom,  self.start, self.end )
        return self.name


class RefGene(CGData.CGDataSetObject):

    def __init__(self):
        self.hugo_map = {}

    def read(self, handle):
        read = csv.reader(handle, delimiter="\t")

        self.hugo_map = {}
        for row in read:
            gene = GeneInfo(
                row[COL_CHROM],
                row[COL_STRAND],
                row[COL_START],
                row[COL_END],
                row[COL_EXCOUNT],
                row[COL_EXSTART],
                row[COL_EXEND],
                row[COL_HUGO])
            if not row[COL_HUGO] in self.hugo_map:
                self.hugo_map[row[COL_HUGO]] = [gene]
            else:
                self.hugo_map[row[COL_HUGO]].append(gene)
        self.chrom_map = {}
        for hugo in self.hugo_map:
            genes = self.hugo_map[hugo]
            for gene in genes:
                if not gene.chrom in self.chrom_map:
                    self.chrom_map[gene.chrom] = []
                self.chrom_map[gene.chrom].append(gene)

        for chrom in self.chrom_map:
            self.chrom_map[chrom].sort(
            lambda x, y: x.chrom_start - y.chrom_start)

    def has_chrom(self, chrom):
        return chrom in self.chrom_map

    def get_chrom(self, chrom):
        return self.chrom_map[chrom]
