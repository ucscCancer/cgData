

import cgData


class bedLine:

    def __init__(self, chrom, chromStart, chromEnd, name,
        score=None, strand=None, thickStart=None, thickEnd=None,
        itemRgb=None, blockCount=None, blockSizes=None, blockStarts=None):

        self.chrom = chrom
        self.chromStart = int(chromStart)
        self.chromEnd = int(chromEnd)
        self.name = name
        self.score = score
        self.strand = strand
        self.thickStart = thickStart
        self.thickEnd = thickEnd
        self.itemRgb = itemRgb
        self.blockCount = blockCount
        self.blockSizes = blockSizes
        self.blockStarts = blockStarts

    def __str__(self):
        return "%s (%s %d-%d)" % (self.name,
                                    self.chrom, self.chromStart, self.chromEnd)

bedColNames = [
"chrom",
"chromStart",
"chromEnd",
"name",
"score",
"strand",
"thickStart",
"thickEnd",
"itemRgb",
"blockCount",
"blockSizes",
"blockStarts",
]


class bedFormatError(Exception):

    def __init__(self, text):
        Exception.__init__(self, text)


class bed(cgData.cgDataSetObject):

    def __init__(self):
        cgData.cgDataSetObject.__init__(self)
        self.bedSize = None
        self.bedArray = []

    def read(self, handle):
        for line in handle:
            tmp = line.rstrip().split('\t')
            if self.bedSize is None:
                self.bedSize = len(tmp)

            if len(tmp) == self.bedSize:
                i = 0
                data = {}
                for val in tmp:
                    data[bedColNames[i]] = val
                    i += 1
                bl = bedLine(**data)
                self.bedArray.append(bl)

    def __iter__(self):
        for v in self.bedArray:
            yield v
