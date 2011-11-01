import CGData


class ClinicalFeature(CGData.CGObjectBase):

    DATA_FORM = CGData.MATRIX

    def __init__(self):
        self._features = None
        super(ClinicalFeature, self).__init__()

    def read(self,handle):
        self._features = {}
        for line in handle:
            tmp = line.rstrip().split("\t")
            if len(tmp) == 3:
                if tmp[0] not in self._features:
                    self._features[tmp[0]] = {}
                if tmp[1] not in self._features[tmp[0]]:
                    self._features[tmp[0]][tmp[1]] = []
                self._features[tmp[0]][tmp[1]].append(tmp[2])

    @property
    def features(self):
        if self._features is None:
            self.load()
        return self._features

class NullClinicalFeature(ClinicalFeature):
    def __init__(self):
        super(NullClinicalFeature, self).__init__()
        self['type'] = 'clinicalFeature'
        self['name'] = '__null__'
        self._features = {}
    def load(self):
        pass
