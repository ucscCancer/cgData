
import CGData


class GenomicSegment(CGData.BaseTable.BaseTable):

    __format__ = {
            "name" : "genomicSegment",
            "type" : "type",
            "form" : "table",
            "columnDef" : [
                "id",
                "chrom",
                "chromStart",
                "chromEnd",
                "strand",
                "value"
            ],
            "groupKey" : "id"
        }

    def __init__(self):
        CGData.BaseTable.BaseTable.__init__(self)
