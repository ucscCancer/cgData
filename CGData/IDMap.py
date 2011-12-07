
import CGData.BaseTable



class IDMap(CGData.BaseTable.BaseTable):
    __format__ = {
            "name" : "idMap",
            "type" : "type",
            "form" : "table",
            "columnDef" : [
                "id",
                "child"
            ],
            "groupKey" : "id",
            "optional" : ["child"]
    }
    
    def __init__(self):
        CGData.BaseTable.BaseTable.__init__(self)
