
import re
import json
from CGData.format import formatTable
from CGData import BaseMatrix, BaseTable


def get_type(type_str):
    if type_str not in formatTable:
        return None
    if formatTable[type_str]['form'] == "matrix":
        return BaseMatrix.get_class(formatTable[type_str])
    if formatTable[type_str]['form'] == "table":
        return BaseTable.get_class(formatTable[type_str])
    return None
    
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
    
    o_type = get_type(meta['type'])
    if o_type is not None:
        out = o_type()
        out.update( meta )
        out.path = data_path
        out.load(data_path)
        return out
    else:
        raise FormatException("%s class not found" % (meta['type']))
