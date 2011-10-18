

import CGData

class DataSubType(CGData.CGDataSetObject):

    DATA_FORM = CGData.TABLE
    COLS = [
        CGData.Column('name', str, primary_key=True),
    ]

    def __init__(self):
        CGData.CGDataSetObject.__init__(self)
