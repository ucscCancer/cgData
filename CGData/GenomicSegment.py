
import CGData


class Segment:

    def __init__(self, chrom, start, end, strand, value):
        self.chrom = chrom.lower()
        if not self.chrom.startswith('chr'):
            self.chrom = 'chr' + self.chrom
        self.chrom_start = start
        self.chrom_end = end
        self.strand = strand
        self.value = value


class GenomicSegment(CGData.CGDataSetObject):

    def __init__(self):
        self.sample_hash = {}

    def read(self, handle):
        self.sample_hash = {}
        for line in handle:
            tmp = line.rstrip().split("\t")
            if not tmp[0] in self.sample_hash:
                self.sample_hash[tmp[0]] = []
            self.sample_hash[tmp[0]].append(
            Segment(tmp[1], int(tmp[2]), int(tmp[3]), tmp[4], float(tmp[5])))

    def __iter__(self):
        for key in self.sample_hash:
            yield key

    def __getitem__(self, i):
        return self.sample_hash[i]
