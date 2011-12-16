
import CGData
import CGData.BaseMatrix

class ClinicalMatrix(CGData.BaseMatrix.BaseMatrix):
    
    __format__ = {
        "name" : "clinicalMatrix",
        "type" : "type",
        "form" : "matrix",
        "rowType" : "idMap",
        "colType" : "clinicalFeature",
        "valueType" : "str",
        "nullString" : ""
    }


    def __init__(self):
        super(ClinicalMatrix, self).__init__()

    def __guess_type__(self, values):
        type = 'float'
        for value in values:
            try:
                a = float(value)
            except ValueError:
                type = 'category'
                break
        return type

