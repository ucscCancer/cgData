
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


