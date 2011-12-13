
import os
import CGData
from glob import glob
import json

class DataSet(dict):
    
    def __init__(self,params={}):
        self.params = params
        self.file_links = None
        self.map_links = None
        super(DataSet,self).__init__()


    def get_file_types(self):
        return self.keys()
    
    def get_map_types(self):
        if self.file_links is None:
            self.build_link_map()
        out = {}
        for ftype in self.file_links:
            for fname in self.file_links[ftype]:
                for pred in self.file_links[ftype][fname]:
                    for mtype in self.file_links[ftype][fname][pred]:
                        out[ mtype ] = True
        return out.keys()
    
    def get_map_links(self,type):
        if self.file_links is None:
            self.build_link_map()
        return self.map_links[type]
    
    def find_map_links(self, map_type=None, map_name=None, predicate=None, file_type=None, file_name=None):
        if self.file_links is None:
            self.build_link_map()
        out = []
        include = [True,True,True,True,True]
        for mtype in self.map_links:
            include[0] = False
            if map_type is None or mtype == map_type:   
                include[0] = True
            for mname in self.map_links[mtype]:
                include[1] = False
                if map_name is None or mname == map_name:
                    include[1] = True
                for mpredicate in self.map_links[mtype][mname]:
                    include[2] = False
                    if predicate is None or mpredicate == predicate:
                        include[2] = True
                    for m_file_type in self.map_links[mtype][mname][mpredicate]:
                        include[3] = False
                        if file_type is None or m_file_type == file_type:
                            include[3] = True
                        for m_file_name in self.map_links[mtype][mname][mpredicate][m_file_type]:
                            include[4] = False
                            if file_name is None or file_name == m_file_name:
                                include[4] = True
                            if False not in include:
                                out.append( { 'type' : m_file_type, 'name' : m_file_name } )
        return out            
    
    def find_file_links(self, file_type=None, file_name=None, predicate=None, map_type=None, map_name=None):
        if self.file_links is None:
            self.build_link_map()
        out = []
        include = [True,True,True,True,True]
        for ftype in self.file_links:
            include[0] = False
            if file_type is None or file_type == ftype:
                include[0] = True
            for fname in self.file_links[ftype]:
                include[1] = False
                if file_name is None or fname == file_name:
                    include[1] = True
                for fpred in self.file_links[ftype][fname]:
                    include[2] = False
                    if predicate is None or fpred == predicate:
                        include[2] = True
                    for mtype in self.file_links[ftype][fname][fpred]:
                        include[3] = False
                        if map_type is None or mtype == map_type:
                            include[3] = True
                        
                        mname = self.file_links[ftype][fname][fpred][mtype]
                        include[4] = False
                        if map_name is None or map_name == mname:
                            include[4] = True
                        
                        if False not in include:
                            out.append( {'type' : mtype, 'name' : mname } )
                            
        return out
    
    def build_link_map(self):
        self.file_links = {}
        self.map_links = {}
        for d_type in self.keys():
            self.file_links[d_type] = {}
            dmap = self.get(d_type)
            for d_name in dmap:
                lmap = dmap[d_name].get_link_map()
                self.file_links[d_type][d_name] = lmap
                
                for pred in lmap:
                    for mtype in lmap[pred]:
                        if mtype not in self.map_links:
                            self.map_links[mtype] = {}
                        mname = lmap[pred][mtype]
                        if mname not in self.map_links[mtype]:
                            self.map_links[mtype][mname] = {}
                        
                        if pred not in self.map_links[mtype][mname]:
                            self.map_links[mtype][mname][pred] = {}
                        
                        if d_type not in self.map_links[mtype][mname][pred]:
                            self.map_links[mtype][mname][pred][d_type] = []
                                
                            self.map_links[mtype][mname][pred][d_type].append(d_name)

    def scan_dirs(self, dirs):
        for dir in dirs:
            CGData.log("SCANNING DIR: %s" % (dir))
            for path in glob(os.path.join(dir, "*")):
                if os.path.isfile(path):
                    if path.endswith(".json"):
                        CGData.log("Found: " + path )
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
