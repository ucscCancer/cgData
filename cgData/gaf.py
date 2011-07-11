#!/usr/bin/python

import cgData
import re

gafHeaders = [
    "Entry Number", "FeatureID", "FeatureType", "FeatureDBSource",
    "FeatureDBVersion", "FeatuerDBDate", "FeatureSeqFileName", "Composite",
    "CompositeType", "CompositeDBSource", "CompositeDBVersion",
    "CompositeDBDate", "AlignmentType", "FeaturedCoordinates",
    "CompositeCoordinates", "Gene", "GeneLocus", "FeatureAliases",
    "FeatureInfo"]

gafCols = [
    "entryNumber", "featureID", "featureType", "featureDBSource",
    "featureDBVersion", "featureDBDate", "featureSeqFileName", "composite",
    "compositeType", "compositeDBSource", "compositeDBVersion",
    "compositeDBDate", "alignmentType", "featureCoordinates",
    "compositeCoordinates", "gene", "geneLocus", "featureAliases",
    "featureInfo"]

reComposite = re.compile(r'chr(\w+):(\w+)-(\w+):(.)')


class gafLine:

    def __init__(
        self, entryNumber, featureID, featureType, featureDBSource,
        featureDBVersion, featureDBDate, featureSeqFileName, composite,
        compositeType, compositeDBSource, compositeDBVersion, compositeDBDate,
        alignmentType, featureCoordinates, compositeCoordinates, gene,
        geneLocus, featureAliases, featureInfo):

        self.name = featureID
        self.entryNumber = entryNumber
        self.featureID = featureID
        self.featureType = featureType
        self.featureDBSource = featureDBSource
        self.featureDBVersion = featureDBVersion
        self.featureDBDate = featureDBDate
        self.featureSeqFileName = featureSeqFileName
        self.composite = composite
        self.compositeType = compositeType
        self.compositeDBSource = compositeDBSource
        self.compositeDBVersion = compositeDBVersion
        self.compositeDBDate = compositeDBDate
        self.alignmentType = alignmentType
        self.featureCoordinates = featureCoordinates
        self.compositeCoordinates = compositeCoordinates
        self.gene = gene
        self.geneLocus = geneLocus
        self.featureAliases = featureAliases
        self.featureInfo = featureInfo

        self.aliases = [gene.split('|')[0]]
        res = reComposite.search(compositeCoordinates)
        if res:
            tmp = res.groups()
            self.chrom = 'chr' + tmp[0]
            self.chromStart = int(tmp[1])
            self.chromEnd = int(tmp[2])
            self.strand = tmp[3]

    def __str__(self):
        return self.featureID


class gaf(cgData.cgDataSetObject):

    def __init__(self):
        cgData.baseObject.__init__(self)
        self.gafData = []

    def read(self, handle, strict=True):
        if strict:
            assert(handle.readline()[:-1].split("\t") == gafHeaders)
        for line in handle:
            line = line.rstrip("\n")
            splitLine = line.split("\t")
            assert(len(splitLine) == len(gafCols))
            self.gafData.append(gafLine(**dict(zip(gafCols, splitLine))))

    def __iter__(self):
        for i in self.gafData:
            yield i
