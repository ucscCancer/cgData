
import csv
import json
import CGData


class Probe(object):

    core_attr = ['name', 'chrom', 'chrom_start', 'chrom_end', 'strand']

    def __init__(self, name, chrom, chrom_start, chrom_end, strand, aliases):
        self.name = name
        self.chrom = chrom
        self.chrom_start = chrom_start
        self.chrom_end = chrom_end
        self.strand = strand
        self.aliases = aliases


class ProbeMap(CGData.CGDataSetObject,CGData.CGGroupMember):

    child_type = Probe
    
    DATA_FORM = CGData.TABLE
    COLS = [
        CGData.Column('name', str, primary_key=True),
        CGData.Column('chrom', str),
        CGData.Column('chrom_start', str),
        CGData.Column('chrom_end', int),
        CGData.Column('strand', str)
    ]

    def __init__(self):
        CGData.CGDataSetObject.__init__(self)
        self.gene_map = None
        self.chrom_map = None

    def read(self, handle):
        self.gene_map = {}
        self.chrom_map = {}
        read = csv.reader(handle, delimiter="\t")
        for line in read:
            self.gene_map[line[0]] = line[1].split(',')
            try:
                self.append(
                Probe(line[0], line[2], int(line[3]),
                    int(line[4]), line[5], self.gene_map[line[0]]))
            except ValueError:
                """location int conversion failed, ignore silently"""
                pass
    def append(self, probe):
        for attr in self.child_type.core_attr:
            if not hasattr(probe, attr):
                raise CGData.FormatException("Missing %s" % (attr))

        if self.chrom_map is None:
            self.chrom_map = {}
        if not probe.chrom in self.chrom_map:
            self.chrom_map[probe.chrom] = {}
        if not probe.name in self.chrom_map[probe.chrom]:
            self.chrom_map[probe.chrom][probe.name] = [probe]
        else:
            self.chrom_map[probe.chrom][probe.name].append(probe)

    def write(self, handle):
        for chrom in self.chrom_map:
            for probeName in self.chrom_map[chrom]:
                probes = self.chrom_map[chrom][probeName]
                for probe in probes:
                    handle.write("%s\n" % ("\t".join([
                        probe.name,
                        ",".join(probe.aliases),
                        probe.chrom,
                        str(probe.chrom_start),
                        str(probe.chrom_end),
                        probe.strand])))
    
    # XXX need a better name. What does this return?
    def lookup(self, item):
        if self.gene_map is None:
            self.load()
        for chrome in self.chrom_map:
            if item in self.chrom_map[chrome]:
                return self.chrom_map[chrome][item]
        return None
    
    def row_iter(self):
        if self.gene_map is None:
            self.load()
        for chrome in self.chrom_map:
            for probe in self.chrom_map[chrome]:
                pset = self.chrom_map[chrome][probe]
                for p in pset:
	                yield (p.name, p.chrom, p.chrom_start, p.chrom_end, p.strand)
    

    # XXX I have no idea what this is returning. What is a pset?
    def get_probes(self):
        if self.gene_map is None:
            self.load()
        for chrome in self.chrom_map:
            for probeSet in self.chrom_map[chrome]:
                for probe in self.chrom_map[chrome][probeSet]:
                    yield probe
