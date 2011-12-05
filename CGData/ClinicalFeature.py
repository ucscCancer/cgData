
import CGData.BaseTable


class ClinicalFeature(CGData.BaseTable.BaseTable):

    __format__ =  {
        "name" : "clinicalFeature",
        "type" : "type",
        "form" : "table",
        "columnDef" : [
            "featureName",
            "predicate",
            "value"
        ],
        "groupKey" : "featureName"
    }
    
    def __init__(self):
        self._features = None
        super(ClinicalFeature, self).__init__()

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
