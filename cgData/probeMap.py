
import csv
import json
import cgData

class probe:
    
    coreAttr = [ 'name', 'chrom', 'chromStart', 'chromEnd', 'strand' ] 
    
    def __init__(self, name, chrom, chromStart, chromEnd, strand):
        self.name = name
        self.chrom = chrom
        self.chromStart = chromStart
        self.chromEnd = chromEnd
        self.strand = strand


class probeMap(cgData.baseObject):
    
    childType = probe
        
    def __init__(self):
        cgData.baseObject( )
        self.geneMap = {}
        self.chromeMap = {}

    def readMeta(self, handle):
        self.attrs = json.loads(handle.read())

    def read(self, handle):
        read = csv.reader(handle, delimiter="\t")
        for line in read:
            self.geneMap[line[0]] = line[1].split(',')
            self.append(
            probe(line[0], line[2], int(line[3]), int(line[4]), line[5])
            )

    def append(self, probe):
        for attr in self.childType.coreAttr:
            if not hasattr( probe, attr ):
                raise cgData.formatException( "Missing %s" % (attr) )
                
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
                    self.chromeMap[chrom][probe].strand
                    ])))
