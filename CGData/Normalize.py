
import CGData.GenomicMatrix
from math import isnan

def floatList(inList):
    """returns only numeric elements of a list"""
    outList = []
    for i in inList:
        try:
            fval = float(i)
            if fval != fval:
                raise ValueError
            outList.append(fval)
        except ValueError:
            continue
    return(outList)

def median(inList):
    """calculates median"""
    cList = floatList(inList)
    cList.sort()
    if len(cList) == 0:
        median = "NA"
    else:
        if len(cList)%2 == 1:
            median = cList[len(cList)/2]
        else:
            median = (cList[len(cList)/2]+cList[(len(cList)/2)-1])/2.0
    return(median)


def row_median_shift(matrix):
    """
    Shift all values in matrix by median value of row (probe)
    """
    out = CGData.GenomicMatrix.GenomicMatrix()
    out.init_blank(cols=matrix.get_col_list(), rows=matrix.get_row_list())
    
    for row in matrix.get_row_list():
        medianVal = median(matrix.get_row(row))
        if medianVal != "NA":
            for col in matrix.get_col_list():
                val = matrix.get_val(col_name=col, row_name=row)
                if not isnan(val):  
                    out.set_val(col_name=col, row_name=row, value=val-medianVal)
    return out

def norm_row_median_shift(matrix, normal_list):
    """
    Shift all non-normal values by median value for  in matrix by median value of row (probe)
    """
    out = CGData.GenomicMatrix.GenomicMatrix()
    out.init_blank(cols=matrix.get_col_list(), rows=matrix.get_row_list())

    col_list = matrix.get_col_list()
    normal_cols = []    
    for norm in normal_list:
        if norm in col_list:
            normal_cols.append(col_list.index(norm))
    
    if len(normal_cols) == 0:
        raise TypeError("No normals found in matrix")
    
    for row in matrix.get_row_list():
        r = matrix.get_row(row)
        normal_row = []
        for i in normal_cols:
            normal_row.append(r[i])
        medianVal = median(normal_row)
        if medianVal == "NA":
            medianVal = 0
        
        for col in matrix.get_col_list():
            val = matrix.get_val(col_name=col, row_name=row)
            if not isnan(val):  
                out.set_val(col_name=col, row_name=row, value=val-medianVal)
    return out