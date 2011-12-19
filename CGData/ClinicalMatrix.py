
import CGData
import CGData.BaseMatrix

from copy import copy

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
    
    
    def transform(self, feat):
        featmap = feat.get_feature_map()
        col_types = []
        for col_name in self.get_col_list():
            if col_name in featmap:
                if 'valueType' in featmap[col_name]:
                    ftype = featmap[col_name]['valueType'][0]
                    if ftype.value == 'float':
                        col_types.append(float)
                    else:
                        col_types.append(str)
                else:
                    col_types.append(str)
            else:
                col_types.append(str)
        return TypedClinicalMatrix(col_types, self)

class TypedClinicalMatrix(ClinicalMatrix):
    def __init__(self, col_types, cmatrix):
        ClinicalMatrix.__init__(self)
        self.matrix = []
        self.col_types = col_types
        self.loaded = True

        for rowname in cmatrix.get_row_list():
            row = []
            for i, col in enumerate(cmatrix.get_row(rowname)):
                if col is not None:
                    row.append( col_types[i](col) )
                else:
                    row.append(None)
            self.matrix.append(row)
        
        self.row_map = copy(cmatrix.row_map)
        self.col_map = copy(cmatrix.col_map)
        

        
    
    


