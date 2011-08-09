
import csv
import CGData
import CGData.TSVMatrix

class TSVMatrix(CGData.CGDataMatrixObject):

    elementType = float
    
    def __init__(self):
        self.colList = None
        self.rowHash = None    

    def read(self, handle, skipVals=False):
        self.colList = {}
        self.rowHash = {}
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
                if not skipVals:
                    self.rowHash[row[0]] = [None] * (len(posHash))
                    for col in posHash:
                        i = posHash[col] + 1
                        if row[i] != 'NA' and row[i] != 'null' and len(row[i]):
                            self.rowHash[row[0]][i - 1] = self.elementType(row[i])
                else:
                    self.rowHash[row[0]] = None
        self.colList = {}
        for sample in posHash:
            self.colList[sample] = posHash[sample]

    def write(self, handle, missing='NA'):
        write = csv.writer(handle, delimiter="\t", lineterminator='\n')
        sampleList = self.getSampleList()
        sampleList.sort(lambda x, y: self.sampleList[x] - self.sampleList[y])
        write.writerow(["probe"] + sampleList)
        for probe in self.rowHash:
            out = [probe]
            for sample in sampleList:
                val = self.rowHash[probe][self.sampleList[sample]]
                if val is None:
                    val = missing
                out.append(val)
            write.writerow(out)

    def getCols(self):
        if self.colList is None:
            self.load( skipVals=True )
        return self.colList.keys()
    
    def getRows(self):
        return self.rowHash.keys()
    
    def getRowVals(self, rowName):
        if self.rowHash is None or self.rowHash[ rowName ] is None:
            self.load( )
        return self.rowHash[ rowName ]

    def colRename(self, oldCol, newCol):
        if oldCol in self.colList:
            self.rowList[newCol] = self.rowList[oldCol]
            del self.sampleList[oldCol]

    def rowRemap(self, oldRow, newRow):
        self.rowHash[newRow] = self.rowHash[oldRow]
        del self.rowHash[oldRow]
        
    def add(self, probe, sample, value):
        if not sample in self.sampleList:
            self.sampleList[sample] = len(self.sampleList)
            for probe in self.rowHash:
                self.rowHash[probe].append(None)

        if not probe in self.rowHash:
            self.rowHash[probe] = [None] * (len(self.sampleList))

        self.rowHash[probe][self.sampleList[sample]] = value

    def join(self, matrix):
        for sample in matrix.sampleList:
            if not sample in self.sampleList:
                self.sampleList[sample] = len(self.sampleList)
                for probe in self.rowHash:
                    self.rowHash[probe].append(None)
            for probe in matrix.rowHash:
                if not probe in self.rowHash:
                    self.rowHash[probe] = [None] * (len(self.sampleList))
                self.rowHash[probe][self.sampleList[sample]] = \
                matrix.rowHash[probe][matrix.sampleList[sample]]
