
import CGData.BaseTable


class ProbeMap(CGData.BaseTable.BaseTable):
    __format__ =  {
            "name" : "probeMap",
            "type" : "type",
            "form" : "table",
            "columnOrder" : [
            "probe",
            "chrom",
            "chrom_start",
            "chrom_end",
            "strand"
            ],
            "primaryKey" : "probe"
        }
        
    def __init__(self):
        CGData.BaseTable.BaseTable.__init__(self)

