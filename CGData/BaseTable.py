
from CGData import CGObjectBase

import csv


class TableRow(object):
    def __init__(self):
        pass
        
    def __str__(self):
        return "<" + ",".join( "%s=%s" % (col, getattr(self,col)) for col in self.__format__['columnOrder']) + ">"

class InvalidFormat(Exception):
    def __init__(self, txt):
        Exception.__init__(self, txt)

class BaseTable(CGObjectBase):
    def __init__(self):
        super(BaseTable,self).__init__()        
        self.__row_class__ = type( "TableRow_" + self['cgformat']['name'], (TableRow,), dict(__format__=self.__format__) )        
        self.free()
    
    def free(self):
        self.firstKey = None
        self.secondKey = None
        self.groupKey = None
        self.loaded = False
        if 'primaryKey' in self['cgformat']:
            self.firstKey = self['cgformat']['primaryKey']
            setattr(self, self['cgformat']['primaryKey'] + "_map", {} )
            self.groupKey = False
        
        #setup the map for groupKeys
        if 'groupKey' in self['cgformat']:
            self.firstKey = self['cgformat']['groupKey']
            setattr(self, self['cgformat']['groupKey'] + "_map", {} )
            self.groupKey = True
        
        if 'secondaryKey' in self['cgformat']:
            self.secondKey = self['cgformat']['secondaryKey']
    
    def read(self, handle):
        cols = self['cgformat']['columnOrder']
        colType = {}
        for col in cols:
            if 'columnDef' in self['cgformat'] and col in self['cgformat']['columnDef'] and 'type' in self['cgformat']['columnDef'][col]:
                if self['cgformat']['columnDef'][col]['type'] == 'float':
                    colType[col] = float
                elif self['cgformat']['columnDef'][col]['type'] == 'int':
                    colType[col] = int
                else:
                    colType[col] = str
            else:
                colType[col] = str
                
        read = csv.reader(handle, delimiter="\t")

        storeMap = getattr(self, self.firstKey + "_map")
        comment = None
        if 'comment' in self['cgformat']:
            comment = self['cgformat']['comment']
        for row in read:
            r = self.__row_class__()
            if comment is None or not row[0].startswith(comment):
                for i, col in enumerate(cols):
                    isOptional = False
                    if 'columnDef' in self['cgformat'] and col in self['cgformat']['columnDef'] and 'optional' in self['cgformat']['columnDef'][col]:
                        isOptional = self['cgformat']['columnDef'][col]['optional']
                    if len(row) > i:
                        setattr(r, col, colType[col](row[i]))
                    else:
                        if isOptional:
                            setattr(r, col, None)
                        else:
                            print row
                            raise InvalidFormat("missing colum " + col)
                            
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
        self.loaded = True
        
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
        if item == "has_" + self.firstKey:
            return self.__get_firstmap__().__contains__
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
        
