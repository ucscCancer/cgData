
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
}


class formatException(Exception):

    def __init__(self, str):
        Exception.__init__(self, str)


class cgObjectBase:

    def __init__(self):
        self.attrs = {}

    def load(self, path):
        dHandle = open(path)
        self.read(dHandle)
        dHandle.close()

        if (os.path.exists(path + ".json")):
            mHandle = open(path + ".json")
            self.setAttrs(json.loads(mHandle.read()))
            mHandle.close()
    
    def store(self, path):
        mHandle = open(path + ".json", "w")
        mHandle.write(json.dumps(self.attrs))
        mHandle.close()
        
        dHandle = open(path, "w")
        self.write(dHandle)
        dHandle.close()            

    def setAttrs(self, attrs):
        self.attrs = attrs
        
        
    def getName(self):
        return self.attrs.get( 'name', None )
    
    def addHistory(self, desc):
        if not 'history' in self.attrs:
            self.attrs[ 'history' ] = []
        self.attrs[ 'history' ].append( desc )



class cgDataSetObject(cgObjectBase):
    
    def __init__(self):
        cgObjectBase.__init__(self)


class cgDataMatrixObject(cgObjectBase):
        
    def __init__(self):
        cgObjectBase.__init__(self)


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
        module = __import__("cgData." + meta['type'])
        submodule = getattr(module, meta['type'])
        cls = getattr(submodule, objectMap[meta['type']])
        out = cls()
        out.load(dataPath)
        return out
    else:
        raise formatException("%s class not found" % (meta['type']))
