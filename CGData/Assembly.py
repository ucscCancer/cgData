
import csv
import CGData


class Assembly(CGData.CGObjectBase):
    """
    Blank Class to represent Genome Assemblies
    """

    DATA_FORM = CGData.TABLE

    COLS = [
        CGData.Column('name', str, primary_key=True),
    ]
