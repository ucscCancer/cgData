
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
    'genomicSegment': 'genomicSegment'
}


class formatException(Exception):
	def __init__(self, str):
		Exception.__init__(self, str)

class baseObject:

    def __init__(self):
        self.attrs = None

    def load(self, path):
        dHandle = open(path)
        self.read(dHandle)
        dHandle.close()

        if (os.path.exists(path + ".json")):
            mHandle = open(path + ".json")
            self.setAttrs(json.loads(mHandle.read()))
            mHandle.close()

    def setAttrs(self, attrs):
        self.attrs = attrs


def load(path):
    if not path.endswith(".json"):
        path = path + ".json"

    dataPath = re.sub(r'.json$', '', path)

    handle = open(path)
    meta = json.loads(handle.read())

    if meta['type'] in objectMap:
        module = __import__("cgData." + meta['type'])
        submodule = getattr(module, meta['type'])
        cls = getattr(submodule, objectMap[meta['type']])
        out = cls()
        out.load(dataPath)
        return out
