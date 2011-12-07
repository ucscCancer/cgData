
import CGData
import CGData.BaseMatrix

from CGData.SQLUtil import *


def sortedSamples(samples):
    import os, re
    # Check for numeric sample ids. Allow for a common prefix
    # before the number.
    prefix = os.path.commonprefix(samples)
    plen = len(prefix)
    if reduce(lambda x,y: x and y, map(lambda s: re.match('^' + prefix + '[0-9]+$', s), samples)):
        return sorted(samples, cmp=lambda x, y: int(x[plen:]) - int(y[plen:]))
    else:
        return sorted(samples)

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

