
import sys
import os
from glob import glob
import json
import cgData
from copy import copy

def log(eStr):
    sys.stderr.write("LOG: %s\n" % (eStr))
    #errorLogHandle.write("LOG: %s\n" % (eStr))


def warn(eStr):
    sys.stderr.write("WARNING: %s\n" % (eStr))
    #errorLogHandle.write("WARNING: %s\n" % (eStr))


def error(eStr):
    sys.stderr.write("ERROR: %s\n" % (eStr))
    #errorLogHandle.write("ERROR: %s\n" % (eStr))


class browserCompiler:

    def __init__(self):
        self.setHash = {}
        self.pathHash = {}

    def scanDirs(self, dirs):
        for dir in dirs:
            log("SCANNING DIR: %s" % (dir))
            for path in glob(os.path.join(dir, "*.json")):
                handle = open(path)
                data = json.loads(handle.read())
                handle.close()
                if 'name' in data and data['name'] is not None\
                and 'type' in data\
                and cgData.has_type(data['type']):
                    if not data['type'] in self.setHash:
                        self.setHash[ data['type'] ] = {}
                        self.pathHash[ data['type'] ] = {}
                        
                    if data['name'] in self.setHash[data['type']]:
                        error("Duplicate %s file %s" % (
                            data['type'], data['name']))
                    self.setHash[data['type']][data['name']] = cgData.lightLoad( path )
                    self.pathHash[data['type']][data['name']] = path
                    log("FOUND: " + data['type'] +
                        "\t" + data['name'] + "\t" + path)
                else:
                    warn("Unknown file type: %s" % (path))
    
    def __iter__(self):
        return self.setHash.__iter__()
    
    def __getitem__(self, i):
        return self.setHash[ i ]
    
    def linkObjects(self):
        """
        Scan found object records and determine if the data they link to is
        avalible
        """
        oMatrix = {}
        for oType in self.setHash:
        	if issubclass( cgData.get_type( oType ), cgData.cgGroupMember ):
        	    gMap = {}
        	    for oName in self.setHash[ oType ]:
        	        oObj = self.setHash[ oType ][ oName ]
        	        if oObj.getGroup() not in gMap:
        	            gMap[ oObj.getGroup() ] = cgData.cgGroupBase( oObj.getGroup() )
        	        gMap[ oObj.getGroup() ].put( oObj )
        	    oMatrix[ oType ] = gMap
        	else:
        	    oMatrix[ oType ] = self.setHash[ oType ]
        
        # Now it's time to check objects for their dependencies
        readyMatrix = {}
        for sType in oMatrix:
            for sName in oMatrix[ sType ]:
                sObj = oMatrix[ sType ][ sName ]
                lMap = sObj.getLinkMap()
                isReady = True
                for lType in lMap:
                    if not oMatrix.has_key( lType ):
                        warn( "%s missing data type %s" % (sName, lType) )
                        isReady = False
                    else:
                        for lName in lMap[ lType ]:
                            if not oMatrix[lType].has_key( lName ):
                                warn( "%s %s missing data %s %s" % ( sType, sName, lType, lName ) )
                                isReady = False
                if not sObj.isLinkReady():
                    warn( "%s %s not LinkReady" % ( sType, sName ) )
                elif isReady:
                    if not sType in readyMatrix:
                        readyMatrix[ sType ] = {}
                    readyMatrix[ sType ][ sName ] = sObj
        
        for rType in readyMatrix:
            log( "READY %s: %s" % ( rType, ",".join(readyMatrix[rType].keys()) ) ) 

        for mergeType in cgData.mergeObjects:
            mObj = cgData.cgNew( mergeType )
            selectTypes = mObj.getTypesSet().keys()
            selectSet = {}
            try:
                for sType in selectTypes:
                    selectSet[ sType ] = readyMatrix[ sType ] 
            except KeyError:
                error("missing data type %s" % (sType) )
                continue
            self.setEnumerate( selectSet )
    
    def setEnumerate( self, a, b={} ):
        """
		This is an recursive function to enumerate possible sets of elements in the 'a' hash
		a is a map of types ('probeMap', 'clinicalMatrix', ...), each of those is a map
        of cgBaseObjects that report getLinkMap requests
        """
        #print "Enter", " ".join( (b[c].getName() for c in b) )
        curKey = None
        for t in a:
            if not t in b:
                curKey = t
        
        if curKey is None:
            print " ".join( ( "%s:%s:%s" % (c, b[c].getName(), str(b[c].getLinkMap()) ) for c in b) )
        else:
            for i in a[curKey]:
                #print "Trying", curKey, i
                c = copy(b)
                sObj = a[curKey][i] #the object selected to be added next
                lMap = sObj.getLinkMap()
                valid = True
                for lType in lMap:
                    if lType in c:
                        if c[lType].getName() not in lMap[lType]:
                            #print c[lType].getName(), "not in", lMap[lType]
                            valid = False
                for sType in c:
                    slMap = c[sType].getLinkMap()
                    for slType in slMap:
                        if curKey == slType:
                            if sObj.getName() not in slMap[slType]:
                                #print a[curKey][i].getName(), "not in",  slMap[slType]
                                valid = False
                if valid:
                    c[ curKey ] = sObj
                    self.setEnumerate( a, c )
    
    
    

