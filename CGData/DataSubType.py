

import CGData.BaseTable

class DataSubType(CGData.BaseTable.BaseTable):


    __format__ = {
        "name" : "dataSubType",
        "type" : "type",
        "form" : "table",
        "columnOrder" : [
        ],
    }

    def __init__(self):
        CGData.BaseTable.BaseTable.__init__(self)
