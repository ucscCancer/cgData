
import os
import re
import json


"""
cgData object style:

Every file type documented in the cgData specification has an equivilent object
to parse and manipulate the contents of that file type. For <dataType> there
should be a cgData.<dataType> object with a <cgData> class. These classes
should extend the baseObject class. For loading they implement the 'read'
function which will parse the contents of a file from a passed file handle.
"""


objectMap = {
    'genomicSegment': 'genomicSegment',
    'genomicMatrix': 'genomicMatrix',
    'probeMap': 'probeMap',
    'sampleMap': 'sampleMap',
    'clinicalMatrix': 'clinicalMatrix',
    'dataSubType': 'dataSubType',
    'track': 'track'
}

mergeObjects = [ 'track' ]

class formatException(Exception):

    def __init__(self, str):
        Exception.__init__(self, str)


def has_type(typeStr):
    return typeStr in objectMap


class cgGroupBase:
    
    def __init__(self):
        pass

class cgObjectBase:

    def __init__(self):
        self.attrs = {}
        self.path = None

    def load(self, path):
        dHandle = open(path)
        self.read(dHandle)
        dHandle.close()
        
        self.path = path
        if (os.path.exists(path + ".json")):
            mHandle = open(path + ".json")
            self.setAttrs(json.loads(mHandle.read()))
            mHandle.close()
    
    def store(self, path):
        mHandle = open(path + ".json", "w")
        mHandle.write(json.dumps(self.attrs))
        mHandle.close()
        
        self.path = path
        dHandle = open(path, "w")
        self.write(dHandle)
        dHandle.close()            

    def setAttrs(self, attrs):
        self.attrs = attrs
    
    def isGroupMember(self):
        if 'group' in self.attrs:
            return True
        return False
    
    def groupName(self):
        return self.attrs.get( 'group', self.attrs.get('name', None))
    
    def getLinkMap(self):
        out = {}
        for key in self.attrs:
            if key.startswith(':'):
                if isinstance( self.attrs[ key ], list ):
                    out[ key[1:] ] = self.attrs[ key ]
                elif self.attrs[ key ] is not None:
                    out[ key[1:] ] = [ self.attrs[ key ] ]
        return out
        
    def getName(self):
        return self.attrs.get( 'name', None )
    
    def addHistory(self, desc):
        if not 'history' in self.attrs:
            self.attrs[ 'history' ] = []
        self.attrs[ 'history' ].append( desc )


class cgMergeObject:
    
    def __init__(self):
        pass
    
    def getTypesSet(self):
        return {}

class cgDataSetObject(cgObjectBase):
    
    def __init__(self):
        cgObjectBase.__init__(self)


class cgDataMatrixObject(cgObjectBase):
        
    def __init__(self):
        cgObjectBase.__init__(self)



class cgSQLObject:
    
    def initSchema(self):
        pass
    
    def genSQL(self):
        pass
    

def cgNew(typeStr):
    module = __import__("cgData." + typeStr)
    submodule = getattr(module, typeStr)
    cls = getattr(submodule, objectMap[typeStr])
    out = cls()
    return out

def load(path):
    if not path.endswith(".json"):
        path = path + ".json"

    dataPath = re.sub(r'.json$', '', path)

    try:
        handle = open(path)
        meta = json.loads(handle.read())
    except IOError:
        raise formatException("Meta-info (%s) file not found" % (path))

    if meta['type'] in objectMap:
        out = cgNew(meta['type'])
        out.setAttrs( meta )
        out.path = dataPath
        out.load(dataPath)
        return out
    else:
        raise formatException("%s class not found" % (meta['type']))


def lightLoad(path):
    if not path.endswith(".json"):
        path = path + ".json"

    dataPath = re.sub(r'.json$', '', path)

    try:
        handle = open(path)
        meta = json.loads(handle.read())
    except IOError:
        raise formatException("Meta-info (%s) file not found" % (path))
        
    if meta['type'] in objectMap:
        out = cgNew(meta['type'])
        out.setAttrs( meta )
        out.path = dataPath
        return out
    else:
        raise formatException("%s class not found" % (meta['type']))
