
import os
import re
import json

objectMap = {
	'genomicSegment' : 'genomicSegment'
}


class baseObject:
	def load( self, path ):
		dHandle = open( path )
		self.read( dHandle )
		dHandle.close()
		
		if ( os.path.exists( path + ".json" ) ):
			mHandle = open( path + ".json" )

def load( path ):
	if not path.endswith( ".json" ):
		path = path + ".json"
	
	dataPath = re.sub( r'.json$', '', path )
	
	handle = open( path )
	meta = json.loads( handle.read() )
	
	if objectMap.has_key( meta['type'] ):
		module = __import__( "cgData." + meta['type'] )
		submodule = getattr( module, meta['type'] )
		cls = getattr( submodule, objectMap[ meta['type'] ] )
		out = cls()
		out.load( dataPath )
		return out	