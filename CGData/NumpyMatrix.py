
import CGData
import numpy
import csv

class NumpyMatrix(CGData.CGDataMatrixObject):
	
    DATA_FORM = CGData.MATRIX
    element_type = float
    corner_name = "row"
    
    null_type = numpy.nan
    
    def __init__(self):
        CGData.CGDataMatrixObject.__init__(self)
        self.row_num = None
        self.col_num = None
        self.matrix = None
        
    
    def read(self, handle, skip_vals=False):
        self.col_num = {}
        self.row_num = {}
        self.matrix = None
        
        pos_hash = None
        col_count = 0
        row_set = []
        for row in csv.reader(handle, delimiter="\t"):
            if pos_hash is None:
                pos_hash = {}
                col_count = 0
                for name in row[1:]:
                    i = 1
                    orig_name = name
                    while name in pos_hash:
                        name = orig_name + "#" + str(i)
                        i += 1
                    pos_hash[name] = col_count
                    col_count += 1                   
            else:
                new_row = [numpy.nan] * col_count
                for col in pos_hash:
                    i = pos_hash[col] + 1
                    if row[i] != 'NA' and row[i] != 'null' and row[i] != 'NONE' and row[i] != "N/A" and len(row[i]):
                        new_row[i - 1] = self.element_type(row[i])
                row_set.append( numpy.array(new_row, dtype=self.element_type) )
                self.row_num[ row[0] ] = len(row_set)-1
        self.matrix = numpy.array( row_set )
        self.col_num = {}
        for col in pos_hash:
            self.col_num[col] = pos_hash[col]

    def write(self, handle, missing='NA'):
        write = csv.writer(handle, delimiter="\t", lineterminator='\n')
        col_list = self.col_num.keys()
        col_list.sort(lambda x, y: self.col_num[x] - self.col_num[y])
        write.writerow([self.corner_name] + col_list)
        for row_name in self.row_num:
            out = [row_name]
            for col in col_list:
                val = self.matrix[self.row_num[row_name]][self.col_num[col]]
                if val == self.null_type or val is None or numpy.isnan(val) or (type(val)==float and math.isnan(val)):
                    val = missing
                out.append(val)
            write.writerow(out)
    
    def row_rename(self, old_row, new_row):
        if new_row != old_row:
            self.row_num[ new_row ] = self.row_num[ old_row ]
            del self.row_num[old_row]

    def remove_null_probes(self, threshold=0.0):
        remove_list = []
        for row_name in self.row_num:
            null_count = 0.0
            for val in self.matrix[self.row_num[row_name]]:
                if val is None or val == self.null_type:
                    null_count += 1.0
            nullPrec = null_count / float(len(self.col_num))
            if 1.0 - nullPrec <= threshold:
                remove_list.append(row_num)
        for name in remove_list:
            self.remove_row(name)
    
  
    def get_row_names(self):
        return self.row_num.keys()
    
    def row_remove(self, row_name):
        print "Remove", row_name
        
        if isinstance(row_name, list):
            del_rows = []
            for n in row_name:
                del_rows.append(self.row_num[n])
            self.matrix = numpy.delete( self.matrix, del_rows, 0)
            for n in row_name:
                row_num = self.row_num[n]
                del self.row_num[n]
                for row in self.row_num:
                    if self.row_num[row] > row_num:
                        self.row_num[row] -= 1
            
        else:
            row_num = self.row_num[ row_name ]
            self.matrix = numpy.delete( self.matrix, row_num, 0)
            del self.row_num[row_name]
            for row in self.row_num:
                if self.row_num[row] > row_num:
                    self.row_num[row] -= 1
        
