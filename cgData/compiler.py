
import sys
import os
from glob import glob
import json
import cgData

def log(eStr):
    sys.stderr.write("LOG: %s\n" % (eStr))
    #errorLogHandle.write("LOG: %s\n" % (eStr))


def warn(eStr):
    sys.stderr.write("WARNING: %s\n" % (eStr))
    #errorLogHandle.write("WARNING: %s\n" % (eStr))


def error(eStr):
    sys.stderr.write("ERROR: %s\n" % (eStr))
    #errorLogHandle.write("ERROR: %s\n" % (eStr))


class browserCompiler:

    def __init__(self):
        self.setHash = {}
        self.pathHash = {}

    def scanDirs(self, dirs):
        for dir in dirs:
            log("SCANNING DIR: %s" % (dir))
            for path in glob(os.path.join(dir, "*.json")):
                handle = open(path)
                data = json.loads(handle.read())
                if 'name' in data and data['name'] is not None\
                and 'type' in data\
                and cgData.has_type(data['type']):
                    if not data['type'] in self.setHash:
                        self.setHash[ data['type'] ] = {}
                        self.pathHash[ data['type'] ] = {}
                        
                    if data['name'] in self.setHash[data['type']]:
                        error("Duplicate %s file %s" % (
                            data['type'], data['name']))
                    self.setHash[data['type']][data['name']] = cgData.lightLoad( path )
                    self.pathHash[data['type']][data['name']] = path
                    log("FOUND: " + data['type'] +
                        "\t" + data['name'] + "\t" + path)
                else:
                    warn("Unknown file type: %s" % (path))
                handle.close()
                
    def linkObjects(self):
        """
        Scan found object records and determin if the data they link to is
        avalible
        """
        for sType in self.setHash:
            for sName in self.setHash[ sType ]:
                sObj = self.setHash[ sType ][ sName ]
                lMap = sObj.getLinkMap()
                isReady = True
                for lType in lMap:
                    if not self.setHash.has_key( lType ):
                        #print "missing data type", lType
                        isReady = False
                    else:
                        for lName in lMap[ lType ]:
                            if not self.setHash[lType].has_key( lName ):
                                #print "missing data", lType, lName
                                isReady = False
                
                if isReady:
                    print "ready", sType, sName
        
        for mergeType in cgData.mergeObjects:
            mObj = cgData.cgNew( mergeType )
            print mObj.getTypesSet()

    def validate(self):
        self.validate_1()
        self.validate_2()

    def validate_1(self):
        removeList = []
        for genomicName in self.setHash['genomic']:
            genomicData = self.setHash['genomic'][genomicName]
            if genomicData['probeMap'] is None:
                error("%s lacks probeMap" % (genomicName))
                removeList.append(genomicName)

            if genomicData['sampleMap'] is None:
                error("%s lacks sampleMap" % (genomicName))
                removeList.append(genomicName)

            if genomicData['probeMap'] in self.setHash['probeMap']:
                probeData = self.setHash['probeMap'][genomicData['probeMap']]
                probeName = genomicData['probeMap']
            else:
                error("%s Missing Probe Data: %s" % (genomicName,
                    genomicData['probeMap']))
                removeList.append(genomicName)

            if genomicData['sampleMap'] in self.setHash['sampleMap']:
                sampleData =\
                self.setHash['sampleMap'][genomicData['sampleMap']]
                sampleName = genomicData['sampleMap']
            else:
                error("%s Missing Sample Data: %s" % (genomicName,
                    genomicData['sampleMap']))
                removeList.append(genomicName)

        print "Remove", removeList
        for remove in removeList:
            if remove in self.setHash['genomic']:
                del self.setHash['genomic'][remove]

    def validate_2(self):
        removeList = []
        for genomicName in self.setHash['genomic']:
            genomeInfo = self.setHash['genomic'][genomicName]
            probeInfo = self.setHash['probeMap'][genomeInfo['probeMap']]
            gPath = self.pathHash['genomic'][genomicName].replace(".json", "")
            gm = cgData.matrix.GeneMatrix()
            try:
                handle = open(gPath)
            except IOError:
                error("unable to open matrix file %s" % (gPath))
                removeList.append(genomicName)
                continue

            gm.read(handle, skipVals=True)
            handle.close()

            sPath = self.pathHash['probeMap'][genomeInfo['probeMap']]
            sPath = sPath.replace(".json", "")
            sm = cgData.sampleMap.SampleMap()
            handle = open(sPath)
            sm.read(handle)
            handle.close()
