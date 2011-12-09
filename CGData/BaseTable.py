
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
        self.firstKey = None
        self.groupKey = None
        self.loaded = False
        if 'primaryKey' in self.__format__:
            self.firstKey = self.__format__['primaryKey']
            setattr(self, self.__format__['primaryKey'] + "_map", {} )
            self.groupKey = False
        
        #setup the map for groupKeys
        if 'groupKey' in self.__format__:
            self.firstKey = self.__format__['groupKey']
            setattr(self, self.__format__['groupKey'] + "_map", {} )
            self.groupKey = True
    
    def read(self, handle):
        cols = self.__format__['columnDef']
        read = csv.reader(handle, delimiter="\t")

        storeMap = getattr(self, self.firstKey + "_map")
        
        for row in read:
            r = self.__row_class__()
            for i, col in enumerate(cols):
                setattr(r, col, row[i])
                if not self.groupKey:
                    storeMap[ getattr(r, self.firstKey ) ] = r
                else:
                    groupName = getattr(r, self.firstKey )
                    if groupName not in storeMap:
                        storeMap[groupName] = []
                    storeMap[groupName].append(r)
    
    def __getattr__(self, item):
        if not self.loaded:
            self.load()

        if item == "get_" + self.firstKey + "_list":
            return self.__get_firstmap__().keys
        if item == "get_by_" + self.firstKey:
            return self.__get_firstmap__().__getitem__                
        if item == "get_" + self.firstKey + "_values":
            return self.__get_firstmap__().values      
        if item == "get_" + self.firstKey + "_map":
            return self.__get_firstmap__
                
        raise AttributeError(item)
    
    def __get_firstmap__(self):
        return getattr(self, self.firstKey + "_map")
    
    def row_iter(self):
        if not self.groupKey:
            keyMap = getattr(self, self.firstKey + "_map")
            for rowKey in keyMap:
                yield keyMap[rowKey]
        else:
            keyMap = getattr(self, self.firstKey + "_map")
            for rowKey in keyMap:
                for elem in keyMap[rowKey]:
                    yield elem
        
