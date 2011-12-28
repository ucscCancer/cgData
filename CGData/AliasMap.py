
import CGData.BaseTable


class AliasMap(CGData.BaseTable.BaseTable):
    __format__ =  {
            "name" : "aliasMap",
            "type" : "type",
            "form" : "table",
            "columnOrder" : [
            "probe",
            "alias"
            ],
            "groupKey" : "probe",
            "links" : {
                "assembly" : {},
                "probe" : {}     
            }
        }
        
    def __init__(self):
        CGData.BaseTable.BaseTable.__init__(self)

