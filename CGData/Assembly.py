
import csv
import CGData

class Assembly(CGData.CGObjectBase):

    DATA_FORM = CGData.TABLE
    
    COLS = [
        CGData.Column('name', str, primary_key=True),
    ]

    def __init__(self):
        pass
