
import CGData.BaseTable



class IDDag(CGData.BaseTable.BaseTable):
    __format__ = {
            "name" : "idDAG",
            "type" : "type",
            "form" : "table",
            "columnOrder" : [
                "id",
                "child"
            ],
            "groupKey" : "id",
            "columnDef" : {
                "child" : { "optional" : True }
            }
    }
    
    def __init__(self):
        CGData.BaseTable.BaseTable.__init__(self)
