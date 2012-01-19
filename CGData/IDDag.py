
import CGData.BaseTable



class IDDag(CGData.BaseTable.BaseTable):
    __format__ = {
            "name" : "idDAG",
            "type" : "type",
            "form" : "table",
            "columnOrder" : [
                "id",
                "child",
                "edgeType"
            ],
            "groupKey" : "id",
            "columnDef" : {
                "child" : { "optional" : True },
                "edgeType" : { "optional" : True }
            }
    }
    
    def __init__(self):
        CGData.BaseTable.BaseTable.__init__(self)



class IDReducer(object):
    def __init__(self, idDag):
        self.revGraph = {}
        for pid in idDag.get_id_list():
            p = idDag.get_by_id(pid)
            for cid in p:
                if cid.child not in self.revGraph:
                    self.revGraph[cid.child] = {}
                self.revGraph[cid.child][cid.id] = cid.edgeType

    def reduce_id(self, id, edgeStop=None):
        outID = id
        while outID in self.revGraph:
            pn = None
            for p in self.revGraph[outID]:
                if edgeStop is None or edgeStop != self.revGraph[outID][p]:
                    pn = p
            if pn is None:
                return outID
            outID = pn
        return outID
    
    def reduce_matrix(self, matrix, edgeStop=None):
        ncols = {}
        rmap = {}
        for col in matrix.get_col_list():
            rval = self.reduce_id(col, edgeStop)
            if rval not in ncols:
                ncols[rval] = []
            ncols[rval].append(col)
            rmap[col] = rval
        out = CGData.GenomicMatrix.GenomicMatrix()
        out.init_blank( cols=ncols.keys(), rows=matrix.get_row_list() )
        
        for row in matrix.get_row_list():
            for col in ncols:
                tmp = []
                for nc in ncols[col]:
                    tmp.append( matrix.get_val( col_name=nc, row_name=row ) )
                v = sum(tmp) / float(len(tmp))
                out.set_val(row_name=row, col_name=col, value=v)
        return out