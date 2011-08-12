#!/usr/bin/python

import re
import CGData

GAF_HEADERS = [
    "Entry Number", "FeatureID", "FeatureType", "FeatureDBSource",
    "FeatureDBVersion", "FeatuerDBDate", "FeatureSeqFileName", "Composite",
    "CompositeType", "CompositeDBSource", "CompositeDBVersion",
    "CompositeDBDate", "AlignmentType", "FeaturedCoordinates",
    "CompositeCoordinates", "Gene", "GeneLocus", "FeatureAliases",
    "FeatureInfo"]

GAF_VARS = [
    "entry_number", "feature_id", "feature_type", "feature_db_source",
    "feature_db_version", "feature_db_date", "feature_seq_file_name", "composite",
    "composite_type", "composite_db_source", "composite_db_version",
    "composite_db_date", "alignment_type", "feature_coordinates",
    "composite_coordinates", "gene", "gene_locus", "feature_aliases",
    "feature_info"]

re_composite = re.compile(r'chr(\w+):(\w+)-(\w+):(.)')


class GafLine:

    def __init__(
        self, entry_number, feature_id, feature_type, feature_db_source,
        feature_db_version, feature_db_date, feature_seq_file_name, composite,
        composite_type, composite_db_source, composite_db_version, composite_db_date,
        alignment_type, feature_coordinates, composite_coordinates, gene,
        gene_locus, feature_aliases, feature_info):

        self.name = feature_id
        self.entry_number = entry_number
        self.feature_id = feature_id
        self.feature_type = feature_type
        self.feature_db_source = feature_db_source
        self.feature_db_version = feature_db_version
        self.feature_db_date = feature_db_date
        self.feature_seq_file_name = feature_seq_file_name
        self.composite = composite
        self.composite_type = composite_type
        self.composite_db_source = composite_db_source
        self.composite_db_version = composite_db_version
        self.composite_db_date = composite_db_date
        self.alignment_type = alignment_type
        self.feature_coordinates = feature_coordinates
        self.composite_coordinates = composite_coordinates
        self.gene = gene
        self.gene_locus = gene_locus
        self.feature_aliases = feature_aliases
        self.feature_info = feature_info

        self.aliases = [gene.split('|')[0]]
        res = re_composite.search(composite_coordinates)
        if res:
            tmp = res.groups()
            self.chrom = 'chr' + tmp[0]
            self.chromStart = int(tmp[1])
            self.chromEnd = int(tmp[2])
            self.strand = tmp[3]

    def __str__(self):
        return self.feature_id


class Gaf(CGData.CGDataSetObject):

    def __init__(self):
        CGData.BaseObject.__init__(self)
        self.gafData = []

    def read(self, handle, strict=True):
        if strict:
            assert(handle.readline()[:-1].split("\t") == GAF_HEADERS)
        for line in handle:
            line = line.rstrip("\n")
            split_line = line.split("\t")
            assert(len(split_line) == len(GAF_VARS))
            self.gafData.append(GafLine(**dict(zip(GAF_VARS, split_line))))

    def __iter__(self):
        for i in self.gafData:
            yield i
