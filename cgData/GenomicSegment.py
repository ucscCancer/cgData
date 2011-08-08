
import cgData


class Segment:

    def __init__(self, chrom, start, end, strand, value):
        self.chrom = chrom.lower()
        if not self.chrom.startswith('chr'):
            self.chrom = 'chr' + self.chrom
        self.chromStart = start
        self.chromEnd = end
        self.strand = strand
        self.value = value


class genomicSegment(cgData.cgDataSetObject):

    def __init__(self):
        self.sampleHash = {}

    def read(self, handle):
        self.sampleHash = {}
        for line in handle:
            tmp = line.rstrip().split("\t")
            if not tmp[0] in self.sampleHash:
                self.sampleHash[tmp[0]] = []
            self.sampleHash[tmp[0]].append(
            Segment(tmp[1], int(tmp[2]), int(tmp[3]), tmp[4], float(tmp[5])))

    def __iter__(self):
        for key in self.sampleHash:
            yield key

    def __getitem__(self, i):
        return self.sampleHash[i]
