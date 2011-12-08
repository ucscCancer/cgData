
import os
import re
import json
import functools
from zipfile import ZipFile
import sys
"""
CGData object style:

Every file type documented in the CGData specification has an equivilent object
to parse and manipulate the contents of that file type. For <dataType> there
should be a CGData.<dataType> object with a <CGData> class. These classes
should extend the baseObject class. For loading they implement the 'read'
function which will parse the contents of a file from a passed file handle.
"""


OBJECT_MAP = {
    'genomicSegment': ('CGData.GenomicSegment', 'GenomicSegment'),
    'genomicMatrix': ('CGData.GenomicMatrix', 'GenomicMatrix'),
    'probeMap': ('CGData.ProbeMap', 'ProbeMap'),
    'aliasMap' : ('CGData.AliasMap', 'AliasMap'),
    'idMap': ('CGData.IDMap', 'IDMap'),
    'clinicalMatrix': ('CGData.ClinicalMatrix', 'ClinicalMatrix'),
    'dataSubType': ('CGData.DataSubType', 'DataSubType'),
    'assembly': ('CGData.Assembly', 'Assembly'),
    'clinicalFeature': ('CGData.ClinicalFeature', 'ClinicalFeature'),
    'refGene' : ('CGData.RefGene', 'RefGene')
}

class FormatException(Exception):

    def __init__(self, str):
        Exception.__init__(self, str)


def has_type(type_str):
    return type_str in OBJECT_MAP

def get_type(type_str):
    mod_name, cls_name = OBJECT_MAP[type_str]
    module = __import__(mod_name, globals(), locals(), [ cls_name ])
    cls = getattr(module, cls_name)
    return cls

class UnimplementedException(Exception):
    def __init__(self, str="Method not implemented"):
        Exception.__init__(self, str)

class CGObjectBase(dict):
    """
    This is the base object for CGData loadable objects.
    The methods covered in the base case cover usage meta-information
    loading/unloading and manipulation as well as zip (cgz) file access.
    """
    def __init__(self):
        self.path = None
        self.zip = None
        self.light_mode = False
        self.loaded = False
        super(CGObjectBase,self).__init__()

    # XXX There are no less than three different code paths for
    # loading the json data, that get hit at different points during
    # the compile. This is really messed up. There's this routine, plus
    # the load and light_load methods, below.
    def load(self, path=None, **kw):
        if path is None and self.path is not None:
            path = self.path
        if path is None:
            raise OSError( "Path not defined" ) 
        
        if self.zip is None:
            if os.path.exists(path):
                dhandle = open(path)
                self.read(dhandle, **kw)
                dhandle.close()
        else:
            z = ZipFile(self.zip)
            dhandle = z.open(self.path)
            self.read(dhandle, **kw)
            dhandle.close()
            z.close()
            
        self.path = path
        if (os.path.exists(path + ".json")):
            mhandle = open(path + ".json")
            meta = json.loads(mhandle.read())
            meta = dict((k, v) for k, v in meta.iteritems() if v != None)
            self.update(meta)
            mhandle.close()
        self.loaded = True

    def unload(self):
        """Call to start freeing up memory"""
        self.free()
        self.loaded = False

    def is_link_ready(self):
        return True
    
    def store(self, path=None):
        if path is None and self.path is not None:
            path = self.path
        if path is None:
            raise OSError( "Path not defined" ) 
        mHandle = open(path + ".json", "w")
        mHandle.write(json.dumps(self))
        mHandle.close()
        if not self.light_mode:
            self.path = path
            dhandle = open(path, "w")
            self.write(dhandle)
            dhandle.close()            
    
    def read(self, handle):
        """
        The read method is implemented by the subclass that 
        inherits from CGObjectBase. It is passed a handle 
        to a file (which may be on file, in a compressed object, or
        from a network source). The implementing class then uses his handle
        to populate it's data structures. 
        """
        raise UnimplementedException()
    
    def write(self, handle):
        """
        The write method is implemented by the subclass that 
        inherits from CGObjectBase. It is passed a handle to an 
        output file, which it can use 'write' method calls to emit
        it's data.
        """
        raise UnimplementedException()

    def get_name(self):
        return self.get( 'cgdata', {} ).get( 'name', None )
    
    def get_type(self):
        return self.get('cgdata', {}).get('type', None)
    
    def get_link_map(self):
        out = {}
        if 'links' in self['cgdata']:
            for link in self['cgdata']['links']:
                if link['type'] not in out:
                    out[ link['type'] ] = []
                out[ link['type'] ].append( link['name'] )
        for e in ['columnKeyMap', 'rowKeyMap' ]:
            if e in self['cgdata']:
                link = self['cgdata'][e]
                if link['type'] not in out:
                    out[ link['type'] ] = []
                out[ link['type'] ].append( link['name'] )

        return out

    def add_history(self, desc):
        if not 'history' in self:
            self[ 'history' ] = []
        self[ 'history' ].append( desc )


class CGDataMatrixObject(CGObjectBase):
        
    def __init__(self):
        CGObjectBase.__init__(self)
    
    
    def get_col_namespace(self):
        """
        Return the name of the column namespace
        """
        raise UnimplementedException()

    def get_row_namespace(self):
        """
        Return the name of the row namespace
        """
        raise UnimplementedException()
    
    def get_col_list(self):
        """
        Returns names of columns
        """
        raise UnimplementedException()
        
    def get_row_list(self):
        """
        Returns names of rows
        """
        raise UnimplementedException()
    
    def get_row_map(self):
        """
        Returns map of row name indexes
        """
        raise UnimplementedException()
         
    def get_col_map(self):
        """
        Returns map of row name indexes
        """
        raise UnimplementedException()
         
    
    def get_row_pos(self, row):
        raise UnimplementedException()
    
    def get_col_pos(self, col):
        raise UnimplementedException()
    
    def get_row_count(self):
        raise UnimplementedException()
        
    def get_col_count(self):
        raise UnimplementedException()
    
    def get_row(self, row_name):
        raise UnimplementedException()

    def get_col(self, col_name):
        raise UnimplementedException()


def cg_new(type_str):
    """
    cg_new takes a type string and creates a new object from the 
    class named, it uses an internally defined map to find all
    official CGData data types. So if a 'genomicMatrix' is requested
    a CGData.GenomicMatrix.GenomicMatrix is initialized.
    
    type_str -- A string name of a CGData type, ie 'genomicMatrix'
    """
    mod_name, cls_name = OBJECT_MAP[type_str]
    module = __import__(mod_name, globals(), locals(), [ cls_name ])
    cls = getattr(module, cls_name)
    out = cls()
    return out

def load(path, zip=None):
    """
    load is a the automatic CGData loading function. There has to 
    be a '.json' file for this function to work. It inspects the 
    '.json' file and uses the 'type' field to determine the 
    appropriate object loader to use. The object is created 
    (using the cg_new function) and the 'read' method is passed
    a handle to the data file. If the 'zip' parameter is not None, 
    then it is used as the path to a zipfile, and the path parameter 
    is used as an path inside the zip file to the object data
    
    path -- path to file (in file system space if zip is None, otherwise
    it is the location in the zip file)
    zip -- path to zip file (None by default)
    """
    if not path.endswith(".json"):
        path = path + ".json"

    data_path = re.sub(r'.json$', '', path)

    try:
        handle = open(path)
        meta = json.loads(handle.read())
    except IOError:
        raise FormatException("Meta-info (%s) file not found" % (path))

    # Throw away empty values
    meta = dict((k, v) for k, v in meta.iteritems() if v != None)

    if meta['type'] in OBJECT_MAP:
        out = cg_new(meta['type'])
        out.update( meta )
        out.path = data_path
        out.load(data_path)
        return out
    else:
        raise FormatException("%s class not found" % (meta['type']))


def light_load(path, zip=None):
    if not path.endswith(".json"):
        path = path + ".json"

    data_path = re.sub(r'.json$', '', path)

    if zip is None:
        try:
            handle = open(path)
            meta = json.loads(handle.read())
        except IOError:
            raise FormatException("Meta-info (%s) file not found" % (path))
    else:
        z = ZipFile(zip)
        handle = z.open(path)
        meta = json.loads(handle.read())
        handle.close()
        z.close()

    # Throw away empty values
    meta = dict((k, v) for k, v in meta.iteritems() if v != None)

    if meta['cgdata']['type'] in OBJECT_MAP:
        out = cg_new(meta['cgdata']['type'])
        out.update( meta )
        out.path = data_path
        out.zip = zip
        out.light_mode = True
        return out
    else:
        raise FormatException("%s class not found" % (meta['cgdata']['type']))

global LOG_LEVEL
LOG_LEVEL = 2

def log(eStr):
    if LOG_LEVEL < 2:
        sys.stderr.write("LOG: %s\n" % (eStr))
        #errorLogHandle.write("LOG: %s\n" % (eStr))


def warn(eStr):
    if LOG_LEVEL < 1:
        sys.stderr.write("WARNING: %s\n" % (eStr))
        #errorLogHandle.write("WARNING: %s\n" % (eStr))


def error(eStr):
    sys.stderr.write("ERROR: %s\n" % (eStr))
    #errorLogHandle.write("ERROR: %s\n" % (eStr))


#####################


TABLE = "table"
MATRIX = "matrix"

class Column(object):
    def __init__(self, name, type, primary_key=False):
        self.name = name
        self.type = type
        self.primary_key = primary_key

