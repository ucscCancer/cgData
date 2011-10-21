
import os
import re
import json
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
    'sampleMap': ('CGData.SampleMap', 'SampleMap'),
    'clinicalMatrix': ('CGData.ClinicalMatrix', 'ClinicalMatrix'),
    'dataSubType': ('CGData.DataSubType', 'DataSubType'),
    'trackGenomic': ('CGData.TrackGenomic', 'TrackGenomic'),
    'trackClinical': ('CGData.TrackClinical', 'TrackClinical'),
    'assembly': ('CGData.Assembly', 'Assembly'),
    'clinicalFeature': ('CGData.ClinicalFeature', 'ClinicalFeature')
}

MERGE_OBJECTS = [ 'trackClinical', 'trackGenomic' ]

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

class CGGroupMember:
    pass

class CGGroupBase:

    def __init__(self, group_name):
        self.members = {}
        self.name = group_name
    
    def __setitem__(self, name, item):
        self.members[ name ] = item
    
    def __getitem__(self, name):
        return self.members[ name ]
    
    def put(self, obj):
        self.members[ obj.get_name() ] = obj
    
    def is_link_ready(self):
        for name in self.members:
            if not self.members[name].is_link_ready():
                return False
        return True
    
    def get_name(self):
        return self.name
    
    def unload(self):
        for name in self.members:
            self.members[name].unload()
    
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
                    
    
    def get_link_map(self):
        out = {}
        for name in self.members:
            lmap = self.members[ name ].get_link_map()
            for ltype in lmap:
                if ltype not in out:
                    out[ ltype ] = []
                for lname in lmap[ltype]:
                    if lname not in out[ltype]:
                        out[ltype].append( lname )
        return out
    

class CGObjectBase(object):

    def __init__(self):
        self.attrs = {}
        self.path = None
        self.zip = None
        self.light_mode = False

    def load(self, path=None, **kw):
        if path is None and self.path is not None:
            path = self.path
        if path is None:
            raise OSError( "Path not defined" ) 
        
        if self.zip is None:
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
            self.set_attrs(json.loads(mhandle.read()))
            mhandle.close()

    def unload(self):
        pass

    def is_link_ready(self):
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
        if not self.light_mode:
            self.path = path
            dhandle = open(path, "w")
            self.write(dhandle)
            dhandle.close()            
            
    def get_attrs(self):
        return self.attrs
    
    def get_attr(self, name):
        return self.attrs.get(name,None)

    def set_attrs(self, attrs):
        self.attrs.update(attrs)
    
    def is_group_member(self):
        if 'group' in self.attrs:
            return True
        return False
    
    def get_group(self):
        return self.attrs.get( 'group', self.attrs.get('name', None))

    def get_name(self):
        return self.attrs.get( 'name', None )
    
    def get_link_map(self):
        out = {}
        for key in self.attrs:
            if key.startswith(':'):
                if isinstance( self.attrs[ key ], list ):
                    out[ key[1:] ] = self.attrs[ key ]
                elif self.attrs[ key ] is not None:
                    out[ key[1:] ] = [ self.attrs[ key ] ]
        return out

    def add_history(self, desc):
        if not 'history' in self.attrs:
            self.attrs[ 'history' ] = []
        self.attrs[ 'history' ].append( desc )


class CGMergeObject(object):
    
    typeSet = {}
    
    def __init__(self):
        self.members = {}
    
    def merge(self, **kw):
        self.members = kw
    
    def __iter__(self):
        return self.members.keys().__iter__()
    
    def __getitem__(self, item):
        return self.members[item]

    def unload(self):
        pass
    
    def gen_sql(self, id_table):
        for t in self.members:
            if issubclass(get_type(t), CGSQLObject):
                for line in self.members[t].gen_sql(id_table):
                    yield line



class CGDataSetObject(CGObjectBase):
    
    def __init__(self):
        CGObjectBase.__init__(self)


class CGDataMatrixObject(CGObjectBase):
        
    def __init__(self):
        CGObjectBase.__init__(self)



class CGSQLObject(object):
    
    def init_schema(self):
        pass
    
    def gen_sql(self, id_table):
        pass
    
    def build_ids(self, id_allocator):
        pass
    

def cg_new(type_str):
    mod_name, cls_name = OBJECT_MAP[type_str]
    module = __import__(mod_name, globals(), locals(), [ cls_name ])
    cls = getattr(module, cls_name)
    out = cls()
    return out

def load(path, zip=None):
    if not path.endswith(".json"):
        path = path + ".json"

    data_path = re.sub(r'.json$', '', path)

    try:
        handle = open(path)
        meta = json.loads(handle.read())
    except IOError:
        raise FormatException("Meta-info (%s) file not found" % (path))

    if meta['type'] in OBJECT_MAP:
        out = cg_new(meta['type'])
        out.set_attrs( meta )
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
        
    if meta['type'] in OBJECT_MAP:
        out = cg_new(meta['type'])
        out.set_attrs( meta )
        out.path = data_path
        out.zip = zip
        out.light_mode = True
        return out
    else:
        raise FormatException("%s class not found" % (meta['type']))



def log(eStr):
    sys.stderr.write("LOG: %s\n" % (eStr))
    #errorLogHandle.write("LOG: %s\n" % (eStr))


def warn(eStr):
    sys.stderr.write("WARNING: %s\n" % (eStr))
    #errorLogHandle.write("WARNING: %s\n" % (eStr))


def error(eStr):
    sys.stderr.write("ERROR: %s\n" % (eStr))
    #errorLogHandle.write("ERROR: %s\n" % (eStr))
