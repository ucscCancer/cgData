
import CGData
import CGData.BaseMatrix

from CGData.SQLUtil import *

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
        self[':clinicalFeature'] = '__null__'

    def is_link_ready(self):
        if self.get( ":sampleMap", None ) == None:
            return False
        return True


    def column(self, name):
        return [ self.row_hash[row][self.col_list[name]] for row in self.row_hash ]

    def __guess_type__(self, values):
        type = 'float'
        for value in values:
            try:
                a = float(value)
            except ValueError:
                type = 'category'
                break
        return [type]

