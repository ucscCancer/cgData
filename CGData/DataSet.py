
import os
import CGData
from glob import glob
import json

class DataSet:
    
    def __init__(self,params={}):
        self.set_hash = {}
        self.params = params

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

                        if (data is not None and 'name' in data 
                        and data['name'] is not None
                        and 'type' in data):                
                            self.addFile(data['type'], data['name'], path)
                    
                    if path.endswith("*.cgz"):
                        cgzList = CGData.CGZ.list( path )
                        for type in cgzList:
                            for zPath in cgzList[type]:
                                self.addFile(type, cgzList[type][zPath], zPath, path)
                if os.path.isdir(path):
                    self.scan_dirs([path])
        
        if "filter" in self.params:
            for t in self.params["filter"]:
                if t in self.set_hash:
                    removeList = []
                    for name in self.set_hash[t]:
                        if not re.search( self.params["filter"][t], name):
                            removeList.append(name)
                    
                    for name in removeList:
                        del self.set_hash[t][name]
                        
    def addFile(self, type, name, path, zipFile=None):
        if CGData.has_type(type):
            if not type in self.set_hash:
                self.set_hash[ type ] = {}
                        
            if name in self.set_hash[type]:
                CGData.error("Duplicate %s file %s" % (
                type, name))
            self.set_hash[type][name] = CGData.light_load( path, zipFile )
            CGData.log("FOUND: " + type +
                "\t" + name + "\t" + path)
        else:
            CGData.warn("Unknown file type: %s" % (path))
                

    def __iter__(self):
        return self.set_hash.__iter__()

    def __getitem__(self, item):
        return self.set_hash[item]

