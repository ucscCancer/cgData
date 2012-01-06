
import os
import CGData
from glob import glob
import json
import re


class DataSetBase(dict):
    
    def get_file_types(self):
        raise CGData.UnimplementedException

    def query(self):
        raise CGData.UnimplementedException


class Link(object):
	def __init__(self, src_type, src_name, predicate, dst_type, dst_name):
		self.src_type = src_type
		self.src_name = src_name
		self.predicate = predicate
		self.dst_type = dst_type
		self.dst_name = dst_name
	
	def __str__(self):
		return "(%s,%s) %s (%s,%s)" % (self.src_type, self.src_name, self.predicate, self.dst_type, self.dst_name)
		

class DataSet(DataSetBase):
    
    def __init__(self,params={}):
        self.params = params
        self.links = None
        super(DataSet,self).__init__()

    def get_file_types(self):
        return self.keys()
    
    def get_map_types(self):
        if self.links is None:
            self.build_link_map()
        out = {}
        for ftype in self.links:
            for fname in self.links[ftype]:
                for pred in self.links[ftype][fname]:
                    for mtype in self.links[ftype][fname][pred]:
                        out[ mtype ] = True
        return out.keys()
    
    def get_map_links(self,type):
        if self.links is None:
            self.build_link_map()
        return self.links[type]
    
    def query(self, src_type=None, src_name=None, predicate=None, dst_type=None, dst_name=None):
        if self.links is None:
            self.build_link_map()
        out = []
        include = [True,True,True,True,True]
        for mtype in self.links:
            include[0] = False
            if src_type is None or mtype == src_type:   
                include[0] = True
            for mname in self.links[mtype]:
                include[1] = False
                if src_name is None or mname == src_name:
                    include[1] = True
                for mpredicate in self.links[mtype][mname]:
                    include[2] = False
                    if predicate is None or mpredicate == predicate:
                        include[2] = True
                    for m_file_type in self.links[mtype][mname][mpredicate]:
                        include[3] = False
                        if dst_type is None or m_file_type == dst_type:
                            include[3] = True
                        for m_file_name in self.links[mtype][mname][mpredicate][m_file_type]:
                            include[4] = False
                            if dst_name is None or dst_name == m_file_name:
                                include[4] = True
                            if False not in include:
								
                                out.append( Link(mtype, mname, mpredicate, m_file_type, m_file_name) )
        return out            
    
    
    def build_link_map(self):
        self.links = {}
        for s_type in self.keys():
            if s_type not in self.links:
                self.links[s_type] = {}
            dmap = self.get(s_type)
            for s_name in dmap:
                if s_name not in self.links[s_type]:
                    self.links[s_type][s_name] = {}
                lmap = dmap[s_name].get_link_map()
                for pred in lmap:
                    d_type = lmap[pred]['type']
                    d_name = lmap[pred]['name']
                    if d_type not in self.links:
                        self.links[d_type] = {}
                    if d_name not in self.links[d_type]:
                        self.links[d_type][d_name] = {}           
                                     
                    if pred not in self.links[s_type][s_name]:
                        self.links[s_type][s_name][pred] = {}
                    if pred not in self.links[d_type][d_name]:
                        self.links[d_type][d_name][pred] = {}
                    
                    if d_type not in self.links[s_type][s_name][pred]:
                        self.links[s_type][s_name][pred][d_type] = {}                               
                    self.links[s_type][s_name][pred][d_type][d_name]= 1
                    
        
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
