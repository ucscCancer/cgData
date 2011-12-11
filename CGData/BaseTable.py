
from CGData import CGObjectBase

import csv


class TableRow(object):
    def __init__(self):
        pass
        
    def __str__(self):
        return "<" + ",".join( "%s=%s" % (col, getattr(self,col)) for col in self.__format__['columnOrder']) + ">"


class BaseTable(CGObjectBase):
    def __init__(self):
        super(BaseTable,self).__init__()        
        self.__row_class__ = type( "TableRow_" + self.__format__['name'], (TableRow,), dict(__format__=self.__format__) )        
        self.free()
    
    def free(self):
        self.firstKey = None
        self.secondKey = None
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
        
        if 'secondaryKey' in self.__format__:
            self.secondKey = self.__format__['secondaryKey']
    
    def read(self, handle):
        cols = self.__format__['columnOrder']
        colType = {}
        for col in cols:
            if 'columnDef' in self.__format__ and col in self.__format__['columnDef']:
                if self.__format__['columnDef'][col]['type'] == 'float':
                    colType[col] = float
                elif self.__format__['columnDef'][col]['type'] == 'int':
                    colType[col] = int
                else:
                    colType[col] = str
            else:
                colType[col] = str
                
        read = csv.reader(handle, delimiter="\t")

        storeMap = getattr(self, self.firstKey + "_map")
        
        for row in read:
            r = self.__row_class__()
            for i, col in enumerate(cols):
                setattr(r, col, colType[col](row[i]))
            if not self.groupKey:
                if self.secondKey is not None:
                    key1 = getattr(r, self.firstKey )                    
                    key2 = getattr(r, self.secondKey )
                    if key1 not in storeMap:
                        storeMap[key1] = {}
                    storeMap[key1][key2] = r
                else:
                    storeMap[ getattr(r, self.firstKey ) ] = r
            else:
                key1 = getattr(r, self.firstKey )
                if self.secondKey is not None:
                    key2 = getattr(r, self.secondKey )
                    if key1 not in storeMap:
                        storeMap[key1] = {}
                    if key2 not in storeMap[key1]:
                        storeMap[key1][key2] = []
                    storeMap[key1][key2].append(r)
                else:
                    if key1 not in storeMap:
                        storeMap[key1] = []
                    storeMap[key1].append(r)
    
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
        
