
import CGData


class Segment(object):

    def __init__(self, sample, chrom, start, end, strand, value):
        self.sample = sample
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
            try:
                start = int(tmp[2])
                stop = int(tmp[3])
            except ValueError:
                #there are examples of segment files with genomic coordinates written like '6.5e+07'
                start = int(float(tmp[2]))
                stop = int(float(tmp[3]))
            self.sample_hash[tmp[0]].append(
            Segment(tmp[0], tmp[1], start, stop, tmp[4], float(tmp[5])))
            
    def get_segments(self):
        for sample in self.sample_hash:
            for segment in self.sample_hash[sample]:
                yield segment
