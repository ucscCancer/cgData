
import CGData.BaseTable


class ProbeMap(CGData.BaseTable.BaseTable):
    __format__ =  {
            "name" : "probeMap",
            "type" : "type",
            "form" : "table",
            "columnDef" : [
            "probeName",
            "aliasList",
            "chrom",
            "chromStart",
            "chromEnd",
            "strand"
            ],
            "primaryKey" : "probeName"
        }
        
    def __init__(self):
        CGData.BaseTable.BaseTable.__init__(self)

