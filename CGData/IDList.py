
import CGData.BaseTable
import CGData.GenomicMatrix
import CGData.ClinicalMatrix


class IDList(CGData.BaseTable.BaseTable):
    __format__ = {
            "name" : "idList",
            "type" : "type",
            "form" : "table",
            "columnOrder" : [
                "id"
            ],
            "primaryKey" : "id"
    }
    
    def __init__(self):
        CGData.BaseTable.BaseTable.__init__(self)


class WhiteLister(object):
    
    def __init__(self, idlist, iddag):
        self.idlist = idlist
        self.iddag = iddag
    
    def whitelist_matrix(self, matrix, whitelist_clinical=False):
        
        if whitelist_clinical:
            idMap = {}
            for name in matrix.get_row_list():
                for pname in self.idlist.get_key_list():
                    if pname==name or self.iddag.is_descendant(pname, name):
                        idMap[name] = pname
            
            col_list = matrix.get_col_list()
            out = CGData.ClinicalMatrix.ClinicalMatrix()
            out.init_blank( rows=idMap.values(), cols=col_list)
            out.update(matrix)
            for name in idMap:
                for feat in col_list:
                    out.set_val( col_name=feat, row_name=idMap[name], value=matrix.get_val(col_name=feat, row_name=name) )

            return out
        
            
        else:        
            idMap = {}
            for name in matrix.get_col_list():
                for pname in self.idlist.get_key_list():
                    if pname==name or self.iddag.is_descendant(pname, name):
                        idMap[name] = pname
            
            row_list = matrix.get_row_list()
            out = CGData.GenomicMatrix.GenomicMatrix()
            out.init_blank( cols=idMap.values(), rows=row_list)
            out.update(matrix)
            for name in idMap:
                for probe in row_list:
                    out.set_val( row_name=probe, col_name=idMap[name], value=matrix.get_val(row_name=probe, col_name=name) )

            return out
        
