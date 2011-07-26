
import cgData

class track(cgData.cgMergeObject):
    def __init__(self):
        pass

    def getTypesSet(self):
        return { 
            'clinicalMatrix' : True, 
            'genomicMatrix' : True,
            'sampleMap' : True,
            'probeMap' : True
        } 
