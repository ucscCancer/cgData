
import CGData.BaseTable



class IDMap(CGData.BaseTable.BaseTable):
    __format__ = {
            "name" : "idMap",
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
