
import csv
import json
import CGData


class Probe:

    coreAttr = ['name', 'chrom', 'chromStart', 'chromEnd', 'strand']

    def __init__(self, name, chrom, chromStart, chromEnd, strand, aliases):
        self.name = name
        self.chrom = chrom
        self.chromStart = chromStart
        self.chromEnd = chromEnd
        self.strand = strand
        self.aliases = aliases


class ProbeMap(CGData.CGDataSetObject,CGData.CGGroupMember):

    childType = Probe

    def __init__(self):
        CGData.CGDataSetObject()
        self.geneMap = None
        self.chromeMap = None

    def readMeta(self, handle):
        self.attrs = json.loads(handle.read())

    def read(self, handle):
        self.geneMap = {}
        self.chromeMap = {}
        read = csv.reader(handle, delimiter="\t")
        for line in read:
            self.geneMap[line[0]] = line[1].split(',')
            self.append(
            Probe(line[0], line[2], int(line[3]),
                int(line[4]), line[5], self.geneMap[line[0]]))

    def append(self, probe):
        for attr in self.childType.coreAttr:
            if not hasattr(probe, attr):
                raise CGData.FormatException("Missing %s" % (attr))

        if not probe.chrom in self.chromeMap:
            self.chromeMap[probe.chrom] = {}
        self.chromeMap[probe.chrom][probe.name] = probe

    def write(self, handle):
        for chrom in self.chromeMap:
            for probe in self.chromeMap[chrom]:
                handle.write("%s\n" % ("\t".join([
                    self.chromeMap[chrom][probe].name,
                    ",".join(self.chromeMap[chrom][probe].aliases),
                    self.chromeMap[chrom][probe].chrom,
                    str(self.chromeMap[chrom][probe].chromStart),
                    str(self.chromeMap[chrom][probe].chromEnd),
                    self.chromeMap[chrom][probe].strand])))
    
    def get(self, item):
        if self.geneMap is None:
            self.load()
        for chrome in self.chromeMap:
            if item in self.chromeMap[chrome]:
                return self.chromeMap[chrome][item]
        return None

    def __iter__(self):
        for chrome in self.chromeMap:
            for probe in self.chromeMap[chrome]:
                yield self.chromeMap[chrome][probe]
    
	def get(self, item):
		for chrome in self.chromeMap:
			if item in self.chromeMap[chrome]:
				return self.chromeMap[chrome][item]
