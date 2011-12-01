
import CGData.format
from CGData import CGObjectBase

import csv


class TableRow(object):
    def __init__(self):
        pass
        
    def __str__(self):
        return "<" + ",".join( "%s=%s" % (col, getattr(self,col)) for col in self.format['columnDef']) + ">"
    
    
def get_class(format):
    tClass = type(format['name'] + "_row", (TableRow,), dict(format=format))
    return type(format['name'], (BaseTable,), dict(format=format, row_class=tClass) )


class BaseTable(CGObjectBase):
    def __init__(self):
        super(BaseTable,self).__init__()
        
        self.primaryKey = None
        self.groupKey = None
        #setup the primary key map
        if 'primaryKey' in self.format:
            self.primaryKey = self.format['primaryKey']
            setattr(self, self.format['primaryKey'] + "_map", {} )
        
        #setup the map for groupKeys
        if 'groupKey' in self.format:
            self.groupKey = self.format['groupKey']
            setattr(self, self.format['groupKey'] + "_group", {} )
    
    def read(self, handle):
        cols = self.format['columnDef']
        read = csv.reader(handle, delimiter="\t")

        primaryMap = None
        if 'primaryKey' in self.format:
            primaryMap = getattr(self, self.format['primaryKey'] + "_map")

        groupMap = None
        if 'groupKey' in self.format:
            primaryMap = getattr(self, self.format['groupKey'] + "_group")

        
        for row in read:
            r = self.row_class()
            for i, col in enumerate(cols):
                setattr(r, col, row[i])
                if primaryMap is not None:
                    primaryMap[ getattr(r, self.format['primaryKey'] ) ] = r
                if groupMap is not None:
                    groupVal = getattr(r, self.format['groupKey'] )
                    if groupVal not in groupMap:
                        groupMap[groupVal] = []
                    groupMap[groupVal].append(r)
    
    def __getattr__(self, item):
        if self.primaryKey is not None:
            if item == "get_" + self.primaryKey + "_list":
                return getattr(self, self.primaryKey + "_map").keys
            if item == "get_by_" + self.primaryKey:
                return getattr(self, self.primaryKey + "_map").__getitem__
        
        if self.groupKey is not None:
            if item == "get_" + self.groupKey + "_list":
                return getattr(self, self.groupKey + "_map").keys
            if item == "get_by_" + self.groupKey:
                return getattr(self, self.groupKey + "_map").__getitem__
                
        raise AttributeError(item)