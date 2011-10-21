
import csv
import CGData


class ClinicalFeature(CGData.CGObjectBase):

    DATA_FORM = CGData.MATRIX

    def __init__(self):
        self.data = None
        super(ClinicalFeature, self).__init__()

    def read(self,handle):
        self.data = {}
        for line in handle:
            tmp = line.rstrip().split("\t")
            if len(tmp) == 3:
                if tmp[0] not in self.data:
                    self.data[tmp[0]] = {}
                if tmp[1] not in self.data[tmp[0]]:
                    self.data[tmp[0]][tmp[1]] = []
                self.data[tmp[0]][tmp[1]].append(tmp[2])
    
    def __iter__(self):
        
        if self.data is None:
            self.load()
        
        return self.data.keys().__iter__()
        
    def __getitem__(self, item):
        return self.data[item]

class NullClinicalFeature(ClinicalFeature):
    def __init__(self):
        super(NullClinicalFeature, self).__init__()
        self['type'] = 'clinicalFeature'
        self['name'] = '__null__'
        self.data = {}
    def load(self):
        pass
