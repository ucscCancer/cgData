

import CGData


class BedLine:

    def __init__(self, chrom, chrom_start, chrom_end, name,
        score=None, strand=None, thick_start=None, thick_end=None,
        item_rgb=None, block_count=None, block_sizes=None, block_starts=None):

        self.chrom = chrom
        self.chrom_start = int(chrom_start)
        self.chrom_end = int(chrom_end)
        self.name = name
        self.score = score
        self.strand = strand
        self.thick_start = thick_start
        self.thick_end = thick_end
        self.item_rgb = item_rgb
        self.block_count = block_count
        self.block_sizes = block_sizes
        self.block_starts = block_starts

    def __str__(self):
        return "%s (%s %d-%d)" % (self.name,
                                    self.chrom, self.chrom_start, self.chrom_end)

BED_COL_NAMES = [
"chrom",
"chrom_start",
"chrom_end",
"name",
"score",
"strand",
"thick_start",
"thick_end",
"item_rgb",
"block_count",
"block_sizes",
"block_starts",
]


class BedFormatError(Exception):

    def __init__(self, text):
        Exception.__init__(self, text)


class Bed(CGData.CGDataSetObject):

    def __init__(self):
        CGData.CGDataSetObject.__init__(self)
        self.bed_size = None
        self.bed_array = []

    def read(self, handle):
        for line in handle:
            tmp = line.rstrip().split('\t')
            if self.bed_size is None:
                self.bed_size = len(tmp)

            if len(tmp) == self.bed_size:
                i = 0
                data = {}
                for val in tmp:
                    data[BED_COL_NAMES[i]] = val
                    i += 1
                bl = BedLine(**data)
                self.bed_array.append(bl)

    def __iter__(self):
        for v in self.bed_array:
            yield v
