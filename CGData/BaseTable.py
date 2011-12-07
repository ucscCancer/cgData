
from CGData import CGObjectBase

import csv


class TableRow(object):
    def __init__(self):
        pass
        
    def __str__(self):
        return "<" + ",".join( "%s=%s" % (col, getattr(self,col)) for col in self.__format__['columnDef']) + ">"


class BaseTable(CGObjectBase):
    def __init__(self):
        super(BaseTable,self).__init__()
        
        self.__row_class__ = type( "TableRow_" + self.__format__['name'], (TableRow,), dict(__format__=self.__format__) )
        
        self.free()
    
    def free(self):
        self.primaryKey = None
        self.groupKey = None
        if 'primaryKey' in self.__format__:
            self.primaryKey = self.__format__['primaryKey']
            setattr(self, self.__format__['primaryKey'] + "_map", {} )
        
        #setup the map for groupKeys
        if 'groupKey' in self.__format__:
            self.groupKey = self.__format__['groupKey']
            setattr(self, self.__format__['groupKey'] + "_map", {} )
    
    def read(self, handle):
        cols = self.__format__['columnDef']
        read = csv.reader(handle, delimiter="\t")

        primaryMap = None
        if 'primaryKey' in self.__format__:
            primaryMap = getattr(self, self.__format__['primaryKey'] + "_map")

        groupMap = None
        if 'groupKey' in self.__format__:
            groupMap = getattr(self, self.__format__['groupKey'] + "_map")

        
        for row in read:
            r = self.__row_class__()
            for i, col in enumerate(cols):
                setattr(r, col, row[i])
                if primaryMap is not None:
                    primaryMap[ getattr(r, self.__format__['primaryKey'] ) ] = r
                if groupMap is not None:
                    groupVal = getattr(r, self.__format__['groupKey'] )
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
    
    def row_iter(self):
        if self.primaryKey is not None:
            keyMap = getattr(self, self.primaryKey + "_map")
            for rowKey in keyMap:
                yield keyMap[rowKey]
        
        if self.groupKey is not None:
            keyMap = getattr(self, self.groupKey + "_map")
            for rowKey in keyMap:
                for elem in keyMap[rowKey]:
                    yield elem
        
