
import csv
import CGData
import CGData.TSVMatrix

class genomicMatrix(CGData.TSVMatrix.TSVMatrix):

    def __init__(self):
        CGData.TSVMatrix.TSVMatrix.__init__(self)
        
    def isLinkReady(self):
        if self.attrs.get( ':sampleMap', None ) is None:
            return False
        return True

    def getProbeList(self):
        return self.getRows()

    def getSampleList(self):
        return self.getCols()

    def sampleRename(self, oldSample, newSample):
        self.colRename( oldSample, newSample )

    def probeRemap(self, oldProbe, newProbe):
        self.rowRename( oldProbe, newProbe )

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

