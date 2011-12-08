
import os
import CGData
from glob import glob
import json

class DataSet(dict):
    
    def __init__(self,params={}):
        self.params = params
        super(DataSet,self).__init__()


    def get_linked_data(self, link_type, link_name):
        out = {}
        for d_type in self.keys():
            dmap = self.get(d_type)
            for d_name in dmap:
                lmap = dmap[d_name].get_link_map()
                if link_type in lmap and link_name in lmap[link_type]:
                    if d_type not in out:
                        out[d_type] = {}
                    out[d_type][d_name] = dmap[d_name]
        return out

    def scan_dirs(self, dirs):
        for dir in dirs:
            CGData.log("SCANNING DIR: %s" % (dir))
            for path in glob(os.path.join(dir, "*")):
                if os.path.isfile(path):
                    if path.endswith(".json"):
                        handle = open(path)
                        try:
                            data = json.loads(handle.read())
                        except ValueError, e:
                            CGData.error("BAD JSON in " + path + " " + str(e) )
                            data = None
                        handle.close()

                        if (data is not None and 'cgdata' in data 
                        and 'name' in data['cgdata']
                        and data['cgdata']['name'] is not None
                        and 'type' in data['cgdata']):
                            self.addFile(data['cgdata']['type'], data['cgdata']['name'], path)

                    if path.endswith("*.cgz"):
                        cgzList = CGData.CGZ.list( path )
                        for type in cgzList:
                            for zPath in cgzList[type]:
                                self.addFile(type, cgzList[type][zPath], zPath, path)
                if os.path.isdir(path):
                    self.scan_dirs([path])

        if "filter" in self.params:
            for t in self.params["filter"]:
                if t in self:
                    removeList = []
                    for name in self[t]:
                        if not re.search( self.params["filter"][t], name):
                            removeList.append(name)

                    for name in removeList:
                        del self[t][name]

    def addFile(self, type, name, path, zipFile=None):
        if CGData.has_type(type):
            if not type in self:
                self[ type ] = {}

            if name in self[type]:
                CGData.error("Duplicate %s file %s" % (
                type, name))
            self[type][name] = CGData.light_load( path, zipFile )
            CGData.log("FOUND: " + type +
                "\t" + name + "\t" + path)
        else:
            CGData.warn("Unknown file type: %s" % (path))
