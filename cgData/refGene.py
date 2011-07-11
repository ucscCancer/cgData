
import csv
import re
import cgData

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
reCommaEnd = re.compile(r',$')


class geneInfo:
    """
    Class to hold information about gene, including exon start/stops
    """

    def __init__(self,
    chrom, strand, start, end, exCount, exStart, exEnd, hugo):
        self.chrom = chrom
        self.strand = strand
        self.chromStart = int(start)
        self.chromEnd = int(end)
        self.exCount = exCount
        self.exStart = []
        for p in reCommaEnd.sub("", exStart).split(','):
            self.exStart.append(int(p))
        self.exEnd = []
        for p in reCommaEnd.sub("", exEnd).split(','):
            self.exEnd.append(int(p))
        self.name = hugo

    def __repr__(self):
        #return "%s_%s_%d_%d" % (self.hugo, self.chrom,  self.start, self.end )
        return self.name


class refGene(cgData.cgDataSetObject):

    def __init__(self):
        self.hugoMap = {}

    def read(self, handle):
        read = csv.reader(handle, delimiter="\t")

        self.hugoMap = {}
        for row in read:
            gene = geneInfo(
                row[COL_CHROM],
                row[COL_STRAND],
                row[COL_START],
                row[COL_END],
                row[COL_EXCOUNT],
                row[COL_EXSTART],
                row[COL_EXEND],
                row[COL_HUGO])
            self.hugoMap[row[COL_HUGO]] = gene

        self.chromMap = {}
        for hugo in self.hugoMap:
            if not self.hugoMap[hugo].chrom in self.chromMap:
                self.chromMap[self.hugoMap[hugo].chrom] = []
            self.chromMap[self.hugoMap[hugo].chrom].append(self.hugoMap[hugo])

        for chrom in self.chromMap:
            self.chromMap[chrom].sort(
            lambda x, y: x.chromStart - y.chromStart)

    def hasChrom(self, chrom):
        return chrom in self.chromMap

    def getChrom(self, chrom):
        return self.chromMap[chrom]
