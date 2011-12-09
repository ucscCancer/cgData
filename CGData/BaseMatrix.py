
import CGData.format


import csv
import CGData
import math


def get_class(format):
    return type(format['name'], (BaseMatrix,), dict(format=format) )


class BaseMatrix(CGData.CGDataMatrixObject):
    
    element_type = str
    null_type = None
    def __init__(self):
        CGData.CGDataMatrixObject.__init__(self)
        self.col_map = None
        self.row_map = None
        self.rows = None
        if self.__format__["valueType"] == 'float':
            self.element_type = float

    def free(self):
        self.col_map = {}
        self.row_map = {}    
        self.rows = []

    def read(self, handle, skip_vals=False):
        self.col_map = {}
        self.row_map = {}    
        self.rows = []
        pos_hash = None
        for row in csv.reader(handle, delimiter="\t"):
            if pos_hash is None:
                pos_hash = {}
                pos = 0
                for name in row[1:]:
                    i = 1
                    orig_name = name
                    while name in pos_hash:
                        name = orig_name + "#" + str(i)
                        i += 1
                    pos_hash[name] = pos
                    pos += 1
            else:
                newRow = []
                if not skip_vals:                    
                    newRow = [self.null_type] * (len(pos_hash))
                    for col in pos_hash:
                        i = pos_hash[col] + 1
                        if row[i] != 'NA' and row[i] != 'null' and row[i] != 'NONE' and row[i] != "N/A" and len(row[i]):
                            newRow[i - 1] = self.element_type(row[i])
                self.row_map[row[0]] = len(self.rows)
                self.rows.append(newRow)
        self.col_map = {}
        for col in pos_hash:
            self.col_map[col] = pos_hash[col]

    def write(self, handle, missing='NA'):
        write = csv.writer(handle, delimiter="\t", lineterminator='\n')
        sample_list = self.col_list.keys()
        sample_list.sort(lambda x, y: self.col_list[x] - self.col_list[y])
        write.writerow([self.corner_name] + sample_list)
        for probe in self.row_hash:
            out = [probe]
            for sample in sample_list:
                val = self.row_hash[probe][self.col_list[sample]]
                if val == self.null_type or val is None or (type(val)==float and math.isnan(val)):
                    val = missing
                out.append(val)
            write.writerow(out)
    
    def get_col_namespace(self):
        """
        Return the name of the column namespace
        """
        return self.get("colNamespace", None)

    def get_row_namespace(self):
        """
        Return the name of the row namespace
        """
        return self.get("rowNamespace", None)
        
    def get_col_list(self):
        """
        Returns names of columns
        """
        if not self.loaded:
            self.load( )
        out = self.col_map.keys()
        out.sort( lambda x,y: self.col_map[x]-self.col_map[y])
        return out 
        
    def get_row_list(self):
        """
        Returns names of rows
        """
        out = self.row_map.keys()
        out.sort( lambda x,y: self.row_map[x]-self.row_map[y])
        return out 
    
    def get_row_pos(self, row):
        return self.row_map[row]
    
    def get_col_pos(self, col):
        return self.col_map[col]
    
    def get_row_count(self):
        return len(self.rows)
        
    def get_col_count(self):
        return len(self.col_map)
    
    def get_row(self, row_name):
        if not self.loaded:
            self.load( )
        return self.rows[ self.row_map[row_name] ]
    
    def get_col(self, col_name):
        if not self.loaded:
            self.load( )
        out = []
        for row_name in self.get_row_list():
            out.append( self.get_val(col_name, row_name) )
        return out
    
    def get_val(self, col, row):
        return self.rows[self.row_map[row]][self.col_map[col]]

    def col_rename(self, old_col, new_col):
        """
        Rename a column
        """
        if old_col in self.col_list:
            self.row_list[new_col] = self.row_list[old_col]
            del self.sample_list[old_col]

    def row_rename(self, old_row, new_row):
        """
        Rename a column
        """
        self.row_hash[new_row] = self.row_hash[old_row]
        del self.row_hash[old_row]
    
    def del_row(self, row):
        """
        Delete a row from the matrix
        """
        del self.row_hash[row]
        
    def del_col(self, col):
        """
        Delete a column from the matrix
        """
        i = self.col_list[col]
        del self.col_list[col]
        for a in self.col_list:
            if self.col_list[a] > i:
                self.col_list[a] -= 1
        for row in self.row_hash:
            del self.row_hash[row][i]
    
    def add(self, col, row, value):
        """
        Put a value into particular cell, adding new 
        columns or rows if needed
        
        col -- name of column
        row -- name of column
        value -- value to be inserted
        """
        if not col in self.col_list:
            self.col_list[col] = len(self.col_list)
            for r in self.row_hash:
                self.row_hash[r].append(self.null_type)

        if not row in self.row_hash:
            self.row_hash[row] = [self.null_type] * (len(self.col_list))

        self.row_hash[row][self.col_list[col]] = value

    def join(self, matrix):
        """
        Insert values from matrix into the current matrix
        """
        for sample in matrix.sample_list:
            if not sample in self.sample_list:
                self.sample_list[sample] = len(self.sample_list)
                for probe in self.row_hash:
                    self.row_hash[probe].append(self.null_type)
            for probe in matrix.row_hash:
                if not probe in self.row_hash:
                    self.row_hash[probe] = [self.null_type] * (len(self.sample_list))
                self.row_hash[probe][self.sample_list[sample]] = \
                matrix.row_hash[probe][matrix.sample_list[sample]]

