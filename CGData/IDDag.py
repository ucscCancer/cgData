
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
        self.graph = None
    
    def _build_graph(self):
        self.graph = {}    
        self.rev_graph = {}    
        for pid in self.get_key_list():
            if pid not in self.graph:
                self.graph[pid] = {}
            p = self.get_by(pid)
            for cid in p:
                self.graph[pid][cid.child] = True
                if cid.child not in self.rev_graph:
                    self.rev_graph[cid.child] = {}
                self.rev_graph[cid.child][cid.id] = True
                
    def is_descendant(self, parent, child):
        if self.graph is None:
            self._build_graph()
        
        cid = child
        while cid in self.rev_graph:
            cid = self.rev_graph[cid].keys()[0]
            if cid == parent:
                return True
        return False
    
    def get_children(self, node):
        if self.graph is None:
            self._build_graph()
        if node in self.graph:
            return self.graph[node]
        return []
    
    def get_parents(self, node):
        if self.graph is None:
            self._build_graph()
        if node in self.rev_graph:
            return self.rev_graph[node]
        return []
        
    def in_graph(self, name):
        if self.graph is None:
            self._build_graph()
        
        if name in self.graph or name in self.rev_graph:
            return True
        return False


class IDReducer(object):
    """
    The IDReducer class uses an IDDag to 'reduce' id's and objects to
    common parent objects.
    
    Assume Matrix 1 has aliquot ids like
        - sample1-aliquot1 
        - sample2-aliquot1 
        - sample2-aliquot1 
    And that Matrix 1 has aliquot ids like
        - sample1-aliquot2 
        - sample2-aliquot2 
        - sample2-aliquot2 
    
    Both files deal with the same samples, but different aliquots were 
    ran on different machines, producing matrices of different datatypes.
    But for data integration perposes, we need to refer to aliquots by their
    parent sample name.
    
    The idDag file for this data would be::
        
        sample1 sample1-aliquot1 
        sample1 sample1-aliquot2 
        sample2 sample2-aliquot1 
        sample2 sample2-aliquot2 
        sample3 sample2-aliquot1 
        sample3 sample2-aliquot2 

    If this file was loaded into an idDag class, and used to initialize an IDReducer
    the following transformatins would be valid::
        
        > idReducer.reduce_id( 'sample1-aliquot1' )
        'sample1'
        > idReducer.reduce_id( 'sample1-aliquot2' )
        'sample1'
    
    """
    def __init__(self, idDag):
        self.revGraph = {}
        for pid in idDag.get_key_list():
            p = idDag.get_by(pid)
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
        out.update(matrix)
        for row in matrix.get_row_list():
            for col in ncols:
                tmp = []
                for nc in ncols[col]:
                    tmp.append( matrix.get_val( col_name=nc, row_name=row ) )
                v = sum(tmp) / float(len(tmp))
                out.set_val(row_name=row, col_name=col, value=v)
        return out
