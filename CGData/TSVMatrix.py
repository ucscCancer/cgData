
import csv
import CGData
import math

class TSVMatrix(CGData.CGDataMatrixObject):

    element_type = str
    corner_name = "row"
    
    null_type = None
    def __init__(self):
        CGData.CGDataMatrixObject.__init__(self)
        self.col_list = None
        self.row_hash = None

    def blank(self):
        self.col_list = {}
        self.row_hash = {}    

    def read(self, handle, skip_vals=False):
        self.col_list = {}
        self.row_hash = {}
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
                if not skip_vals:
                    self.row_hash[row[0]] = [self.null_type] * (len(pos_hash))
                    for col in pos_hash:
                        i = pos_hash[col] + 1
                        if row[i] != 'NA' and row[i] != 'null' and row[i] != 'NONE' and row[i] != "N/A" and len(row[i]):
                            self.row_hash[row[0]][i - 1] = self.element_type(row[i])
                else:
                    self.row_hash[row[0]] = None
        self.col_list = {}
        for sample in pos_hash:
            self.col_list[sample] = pos_hash[sample]

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
    
    def get_x_namespace(self):
        return self.attrs.get("xNamespace", None)

    def get_y_namespace(self):
        return self.attrs.get("yNamespace", None)
        
    def get_x_names(self):
        return self.get_cols()
    
    def get_y_names(self):
        return self.get_rows()
    
    def get_cols(self):
        if self.col_list is None:
            self.load( skip_vals=True )
        out = self.col_list.keys()
        out.sort( lambda x,y: self.col_list[x]-self.col_list[y])
        return out 
        
    def get_rows(self):
        return self.row_hash.keys()
    
    def get_row_vals(self, row_name):
        if self.row_hash is None or self.row_hash[ row_name ] is None:
            self.load( )
        return self.row_hash[ row_name ]
    
    def get(self, col, row):
        return self.row_hash[row][self.col_list[col]]

    def col_rename(self, old_col, new_col):
        if old_col in self.col_list:
            self.row_list[new_col] = self.row_list[old_col]
            del self.sample_list[old_col]

    def row_rename(self, old_row, new_row):
        self.row_hash[new_row] = self.row_hash[old_row]
        del self.row_hash[old_row]
    
    def del_row(self, row):
        del self.row_hash[row]
        
    def del_col(self, col):
        i = self.col_list[col]
        del self.col_list[col]
        for a in self.col_list:
            if self.col_list[a] > i:
                self.col_list[a] -= 1
        for row in self.row_hash:
            del self.row_hash[row][i]
    
    def add(self, col, row, value):
        if not col in self.col_list:
            self.col_list[col] = len(self.col_list)
            for r in self.row_hash:
                self.row_hash[r].append(self.null_type)

        if not row in self.row_hash:
            self.row_hash[row] = [self.null_type] * (len(self.col_list))

        self.row_hash[row][self.col_list[col]] = value

    def join(self, matrix):
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

    def unload(self):
        self.col_list = None
        self.row_hash = None
