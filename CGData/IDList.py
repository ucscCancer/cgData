
import CGData.BaseTable


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
    
    def whitelist_matrix(self, matrix):
        
        idMap = {}
        for name in matrix.get_col_list():
            for pname in self.idlist.get_id_list():
                if pname==name or self.iddag.is_descendant(pname, name):
                    idMap[name] = pname
        
        row_list = matrix.get_row_list()
        out = CGData.GenomicMatrix.GenomicMatrix()
        out.init_blank( cols=idMap.values(), rows=row_list)
        
        for name in idMap:
            for probe in row_list:
                out.set_val( row_name=probe, col_name=idMap[name], value=matrix.get_val(row_name=probe, col_name=name) )

        return out
    
