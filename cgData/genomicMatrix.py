
import csv
import cgData


class genomicMatrix(cgData.cgDataMatrixObject,cgData.cgSQLObject):

    def __init__(self):
        cgData.cgDataMatrixObject.__init__(self)
        self.probeHash = {}
        self.sampleList = {}

    def read(self, handle, skipVals=False):
        self.sampleList = {}
        self.probeHash = {}
        posHash = None
        for row in csv.reader(handle, delimiter="\t"):
            if posHash is None:
                posHash = {}
                pos = 0
                for name in row[1:]:
                    i = 1
                    origName = name
                    while name in posHash:
                        name = origName + "#" + str(i)
                        i += 1
                    posHash[name] = pos
                    pos += 1
            else:
                self.probeHash[row[0]] = [None] * (len(posHash))
                if not skipVals:
                    for sample in posHash:
                        i = posHash[sample] + 1
                        if row[i] != 'NA' and row[i] != 'null' and len(row[i]):
                            self.probeHash[row[0]][i - 1] = float(row[i])
        self.sampleList = {}
        for sample in posHash:
            self.sampleList[sample] = posHash[sample]

    def write(self, handle, missing='NA'):
        write = csv.writer(handle, delimiter="\t", lineterminator='\n')
        sampleList = self.getSampleList()
        sampleList.sort(lambda x, y: self.sampleList[x] - self.sampleList[y])
        write.writerow(["probe"] + sampleList)
        for probe in self.probeHash:
            out = [probe]
            for sample in sampleList:
                val = self.probeHash[probe][self.sampleList[sample]]
                if val is None:
                    val = missing
                out.append(val)
            write.writerow(out)

    def getProbeList(self):
        return self.probeHash.keys()

    def getSampleList(self):
        return self.sampleList.keys()

    def sampleRename(self, oldSample, newSample):
        if oldSample in self.sampleList:
            self.sampleList[newSample] = self.sampleList[oldSample]
            del self.sampleList[oldSample]

    def probeRemap(self, oldProbe, newProbe):
        self.probeHash[newProbe] = self.probeHash[oldProbe]
        del self.probeHash[oldProbe]

    def remap(self, altMap, skipMissing=False):
        validMap = {}
        for alt in altMap:
            validMap[alt.aliases[0]] = True
            if not skipMissing or alt.name in self.probeHash:
                self.probeRemap(alt.name, alt.aliases[0])
        if skipMissing:
            removeList = []
            for name in self.probeHash:
                if not name in validMap:
                    removeList.append(name)
            for name in removeList:
                del self.probeHash[name]

    def removeNullProbes(self, threshold=0.0):
        removeList = []
        for probe in self.probeHash:
            nullCount = 0.0
            for val in self.probeHash[probe]:
                if val is None:
                    nullCount += 1.0
            nullPrec = nullCount / float(len(self.probeHash[probe]))
            if 1.0 - nullPrec <= threshold:
                removeList.append(probe)
        for name in removeList:
            del self.probeHash[name]

    def writeGCT(self, handle, missing=''):
        write = csv.writer(handle, delimiter="\t", lineterminator='\n')
        sampleList = self.getSampleList()
        sampleList.sort(lambda x, y: self.sampleList[x] - self.sampleList[y])
        write.writerow(["#1.2"])
        write.writerow([len(self.probeHash), len(sampleList)])
        write.writerow(["NAME", "Description"] + sampleList)
        for probe in self.probeHash:
            out = [probe, probe]
            for sample in sampleList:
                val = self.probeHash[probe][self.sampleList[sample]]
                if val is None:
                    val = missing
                out.append(val)
            write.writerow(out)

    def add(self, probe, sample, value):
        if not sample in self.sampleList:
            self.sampleList[sample] = len(self.sampleList)
            for probe in self.probeHash:
                self.probeHash[probe].append(None)

        if not probe in self.probeHash:
            self.probeHash[probe] = [None] * (len(self.sampleList))

        self.probeHash[probe][self.sampleList[sample]] = value

    def join(self, matrix):
        for sample in matrix.sampleList:
            if not sample in self.sampleList:
                self.sampleList[sample] = len(self.sampleList)
                for probe in self.probeHash:
                    self.probeHash[probe].append(None)
            for probe in matrix.probeHash:
                if not probe in self.probeHash:
                    self.probeHash[probe] = [None] * (len(self.sampleList))
                self.probeHash[probe][self.sampleList[sample]] = \
                matrix.probeHash[probe][matrix.sampleList[sample]]




    def initSchema(self):
        CREATE_BED = """
CREATE TABLE %s (
    bin smallint unsigned not null,
    chrom varchar(255) not null,
    chromStart int unsigned not null,
    chromEnd int unsigned not null,
    name varchar(255) not null,
    score int not null,
    strand char(1) not null,
    thickStart int unsigned not null,
    thickEnd int unsigned not null,
    reserved int unsigned  not null,
    blockCount int unsigned not null,
    blockSizes longblob not null,
    chromStarts longblob not null,
    expCount int unsigned not null,
    expIds longblob not null,
    expScores longblob not null,
    INDEX(name(16)),
    INDEX(chrom(4),chromStart),
    INDEX(chrom(4),bin)
);
"""
