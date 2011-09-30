
import csv
import json
import CGData


class Probe:

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

    def __init__(self):
        CGData.CGDataSetObject.__init__(self)
        self.gene_map = None
        self.chrom_map = None

    def read_meta(self, handle):
        self.attrs = json.loads(handle.read())

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
    
    def get(self, item):
        if self.gene_map is None:
            self.load()
        for chrome in self.chrom_map:
            if item in self.chrom_map[chrome]:
                return self.chrom_map[chrome][item]
        return None

    def __iter__(self):
        if self.gene_map is None:
            self.load()
        for chrome in self.chrom_map:
            for probe in self.chrom_map[chrome]:
                yield self.chrom_map[chrome][probe]
    
    def get(self, item):
        if self.gene_map is None:
            self.load()
        for chrome in self.chrom_map:
            if item in self.chrom_map[chrome]:
                return self.chrom_map[chrome][item]
