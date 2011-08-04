
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
    'track': 'track',
    'assembly':'assembly',
    'clinicalFeature':'clinicalFeature'
}

mergeObjects = [ 'track' ]

class formatException(Exception):

    def __init__(self, str):
        Exception.__init__(self, str)


def has_type(typeStr):
    return typeStr in objectMap

def get_type(typeStr):

    module = __import__("cgData." + typeStr)
    submodule = getattr(module, typeStr)
    cls = getattr(submodule, objectMap[typeStr])
    return cls


class cgGroupMember:
    pass

class cgGroupBase:

    def __init__(self, groupName):
        self.members = {}
        self.name = groupName
    
    def __setitem__(self, name, item):
        self.members[ name ] = item
    
    def __getitem__(self, name):
        return self.members[ name ]
    
    def put(self, obj):
        self.members[ obj.getName() ] = obj
    
    def isLinkReady(self):
        for name in self.members:
            if not self.members[name].isLinkReady():
                return False
        return True
    
    def getName(self):
        return self.name
    
    def get(self, **kw):
		for elem in self.members:
			found = True
			obj = self.members[ elem ]
			for key in kw:
				if obj.attrs.get( key, None ) != kw[key]\
				and obj.attrs.get( ":" + key, None ) != kw[key]:
					found = False
			if found:
				return obj
					
    
    def getLinkMap(self):
        out = {}
        for name in self.members:
            lMap = self.members[ name ].getLinkMap()
            for lType in lMap:
                if lType not in out:
                    out[ lType ] = []
                for lName in lMap[lType]:
                    if lName not in out[lType]:
                        out[lType].append( lName )
        return out
    

class cgObjectBase:

    def __init__(self):
        self.attrs = {}
        self.path = None
        self.lightMode = False

    def load(self, path=None, **kw):
        if path is None and self.path is not None:
            path = self.path
        if path is None:
            raise OSError( "Path not defined" ) 
        dHandle = open(path)
        self.read(dHandle, **kw)
        dHandle.close()
        
        self.path = path
        if (os.path.exists(path + ".json")):
            mHandle = open(path + ".json")
            self.setAttrs(json.loads(mHandle.read()))
            mHandle.close()

    def isLinkReady(self):
        return True
    
    def store(self, path=None):
        if path is None and self.path is not None:
            path = self.path
        if path is None:
            raise OSError( "Path not defined" ) 
        mHandle = open(path + ".json", "w")
        mHandle.write(json.dumps(self.attrs))
        mHandle.close()
        print path
        if not self.lightMode:
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
    
    def getGroup(self):
        return self.attrs.get( 'group', self.attrs.get('name', None))

    def getName(self):
        return self.attrs.get( 'name', None )
    
    def getLinkMap(self):
        out = {}
        for key in self.attrs:
            if key.startswith(':'):
                if isinstance( self.attrs[ key ], list ):
                    out[ key[1:] ] = self.attrs[ key ]
                elif self.attrs[ key ] is not None:
                    out[ key[1:] ] = [ self.attrs[ key ] ]
        return out

    def addHistory(self, desc):
        if not 'history' in self.attrs:
            self.attrs[ 'history' ] = []
        self.attrs[ 'history' ].append( desc )


class cgMergeObject:
    
    typeSet = {}
    
    def __init__(self):
        self.members = {}
    
    def merge(self, **kw):
        self.members = kw



class cgDataSetObject(cgObjectBase):
    
    def __init__(self):
        cgObjectBase.__init__(self)


class cgDataMatrixObject(cgObjectBase):
        
    def __init__(self):
        cgObjectBase.__init__(self)



class cgSQLObject:
    
    def initSchema(self):
        pass
    
    def genSQL(self, idTable):
        pass
    
    def buildIDs(self, idAllocator):
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
        out.lightMode = True
        return out
    else:
        raise formatException("%s class not found" % (meta['type']))
