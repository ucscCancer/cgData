
import sys
import os
from glob import glob
import json
from copy import copy
import CGData
import CGData.CGZ
from CGData import log, error, warn
import re

class CGIDTable:
    
    def __init__(self):
        self.id_table = {}
    
    def get( self, itype, iname ):
        if itype not in self.id_table:
            self.id_table[ itype ] = {}
        if iname not in self.id_table[ itype ]:
            self.id_table[ itype ][ iname ] = len( self.id_table[ itype ] )
            
        return self.id_table[ itype ][ iname ]


class BrowserCompiler:
    
    PARAMS = [ "compiler.mode" ]

    def __init__(self,params={}):
        self.set_hash = {}
        self.out_dir = "out"
        self.params = params
        if self.params['binary']:
            CGData.OBJECT_MAP['trackGenomic'] = ('CGData.TrackGenomic', 'BinaryTrackGenomic')

    def scan_dirs(self, dirs):
        for dir in dirs:
            log("SCANNING DIR: %s" % (dir))
            for path in glob(os.path.join(dir, "*")):
                if os.path.isfile(path):
                    if path.endswith(".json"):
                        handle = open(path)
                        try:
                            data = json.loads(handle.read())
                        except ValueError, e:
                            error("BAD JSON in " + path + " " + str(e) )
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
                error("Duplicate %s file %s" % (
                type, name))
            self.set_hash[type][name] = CGData.light_load( path, zipFile )
            log("FOUND: " + type +
                "\t" + name + "\t" + path)
        else:
            warn("Unknown file type: %s" % (path))
            
    
    
    def __iter__(self):
        return self.set_hash.__iter__()
    
    def __getitem__(self, i):
        return self.set_hash[ i ]
    
    def link_objects(self):
        """
        Scan found object records and determine if the data they link to is
        avalible
        """
        omatrix = {}
        for otype in self.set_hash:
            if issubclass( CGData.get_type( otype ), CGData.CGGroupMember ):
                gmap = {}
                for oname in self.set_hash[ otype ]:
                    oobj = self.set_hash[ otype ][ oname ]
                    if oobj.get_group() not in gmap:
                        gmap[ oobj.get_group() ] = CGData.CGGroupBase( oobj.get_group() )
                    gmap[ oobj.get_group() ].put( oobj )
                omatrix[ otype ] = gmap
            else:
                omatrix[ otype ] = self.set_hash[ otype ]
        
        # Now it's time to check objects for their dependencies
        ready_matrix = {}
        for stype in omatrix:
            for sname in omatrix[ stype ]:
                sobj = omatrix[ stype ][ sname ]
                lmap = sobj.get_link_map()
                is_ready = True
                for ltype in lmap:
                    if not omatrix.has_key( ltype ):
                        warn( "%s missing data type %s" % (sname, ltype) )
                        is_ready = False
                    else:
                        for lname in lmap[ ltype ]:
                            if not omatrix[ltype].has_key( lname ):
                                warn( "%s %s missing data %s %s" % ( stype, sname, ltype, lname ) )
                                is_ready = False
                if not sobj.is_link_ready():
                    warn( "%s %s not LinkReady" % ( stype, sname ) )
                elif is_ready:
                    if not stype in ready_matrix:
                        ready_matrix[ stype ] = {}
                    ready_matrix[ stype ][ sname ] = sobj
        
        for rtype in ready_matrix:
            log( "READY %s: %s" % ( rtype, ",".join(ready_matrix[rtype].keys()) ) )         

        for dType in ready_matrix:
            log("Found %s %d" % (dType, len(ready_matrix[dType])))
            
        merge_children = {}

        for merge_type in CGData.MERGE_OBJECTS:
            mtype = CGData.get_type( merge_type )
            print mtype
            select_types = mtype.typeSet
            select_set = {}
            try:
                for stype in select_types:
                    select_set[ stype ] = ready_matrix[ stype ] 
                    if stype not in merge_children:
                        merge_children[stype] = {}
            except KeyError:
                error("missing data type %s" % (stype) )
                continue
            mobjlist = self.set_enumerate( mtype, select_set )
            for mobj in mobjlist:
                if merge_type not in ready_matrix:
                    ready_matrix[ merge_type ] = {}
                for cType in mobj:
                    merge_children[cType][mobj[cType].get_name()] = True
                ready_matrix[ merge_type ][ mobj.get_name() ] = mobj
        
        self.compile_matrix = {}
        for sType in ready_matrix:
            self.compile_matrix[sType] = {}
            for name in ready_matrix[sType]:
                if sType not in merge_children or name not in merge_children[sType]:
                    self.compile_matrix[sType][name] = ready_matrix[sType][name]
       
        log("After Merge")
        for dType in ready_matrix:
            log("Found %s %d" % (dType, len(self.compile_matrix[dType])))
        
    def set_enumerate( self, merge_type, a, b={} ):
        """
        This is an recursive function to enumerate possible sets of elements in the 'a' hash
        a is a map of types ('probeMap', 'clinicalMatrix', ...), each of those is a map
        of cgBaseObjects that report get_link_map requests
        """
        #print "Enter", " ".join( (b[c].get_name() for c in b) )
        cur_key = None
        for t in a:
            if not t in b:
                cur_key = t
        
        if cur_key is None:
            #make sure selected subgraph is connected
            #start by building a graph of connections
            #and map of connected nodes
            cMap = {}
            lMap = {}
            for c in b:
            	n = "%s:%s" % (c, b[c].get_name())
            	cMap[ n ] = False
            	lMap[n] = {}
            	for d in b[c].get_link_map():
            		for e in b[c].get_link_map()[d]:
	            		m = "%s:%s" % (d,e)
    	        		lMap[n][m] = True
    	    #add the first node to the connected set
    	    cMap[ cMap.keys()[0] ] = True
    	    found = True
    	    #continue adding nodes to the connected set, until no more can be found
    	    while found:
    	    	found = False
    	    	for c in cMap:
    	    		if not cMap[c]:
    	    			for d in cMap:
    	    				if cMap[d]:
    	    					if d in lMap[c] or c in lMap[d]:
    	    						found = True
    	    						cMap[c] = True
    	    						cMap[d] = True
            
            #if there are no disconnected nodes, then the subset represents a connected graph,
            #and is ready to merge
            if cMap.values().count(False) == 0:
	            #print " ".join( ( "%s:%s:%s" % (c, b[c].get_name(), str(b[c].get_link_map()) ) for c in b) )
	            log( "Merging %s" % ",".join( ( "%s:%s" %(c,b[c].get_name()) for c in b) ) )  
	            mergeObj = merge_type()
	            mergeObj.merge( **b )
	            return [ mergeObj ]
        else:
            out = []
            for i in a[cur_key]:
                #print "Trying", cur_key, i
                c = copy(b)
                sobj = a[cur_key][i] #the object selected to be added next
                lmap = sobj.get_link_map()
                valid = True
                for ltype in lmap:
                    if ltype in c:
                        if c[ltype].get_name() not in lmap[ltype]:
                            #print c[ltype].get_name(), "not in", lmap[ltype]
                            valid = False
                for stype in c:
                    slmap = c[stype].get_link_map()
                    for sltype in slmap:
                        if cur_key == sltype:
                            if sobj.get_name() not in slmap[sltype]:
                                #print a[cur_key][i].get_name(), "not in",  slmap[sltype]
                                valid = False
                if valid:
                    c[ cur_key ] = sobj
                    out.extend( self.set_enumerate( merge_type, a, c ) )
            return out
        return []

    def gen_sql(self):
        if "compiler.mode" in self.params and self.params[ "compiler.mode" ] == "scan":
            return
        log( "Writing SQL" )     
        if not os.path.exists(self.out_dir):
            os.makedirs(self.out_dir)
        self.id_table = CGIDTable()
        for rtype in self.compile_matrix:
            if issubclass( CGData.get_type( rtype ), CGData.CGSQLObject ):
                for rname in self.compile_matrix[ rtype ]:
                    shandle = self.compile_matrix[ rtype ][ rname ].gen_sql( self.id_table )
                    if shandle is not None:
                        ohandle = open( os.path.join( self.out_dir, "%s.%s.sql" % (rtype, rname ) ), "w" )
                        for line in shandle:
                            ohandle.write( line )
                        ohandle.close()
                    #tell the object to unload data, so we don't continually allocate over the compile
                    self.compile_matrix[ rtype ][ rname ].unload()
    
    

