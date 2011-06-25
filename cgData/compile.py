
import sys
import os
from glob import glob
import json
import cgData.matrix
import cgData.sampleMap

def log(eStr):
	sys.stderr.write("LOG: %s\n" % (eStr) )
	#errorLogHandle.write( "LOG: %s\n" % (eStr) )

def warn(eStr):
	sys.stderr.write("WARNING: %s\n" % (eStr) )
	#errorLogHandle.write( "WARNING: %s\n" % (eStr) )

def error(eStr):
	sys.stderr.write("ERROR: %s\n" % (eStr) )
	#errorLogHandle.write( "ERROR: %s\n" % (eStr) )


class BrowserCompile:
	def __init__(self):
		self.setHash = {  'genomic' : {}, "clinical" : {}, "probeMap" : {}, "sampleMap" : {} }
		self.pathHash = {  'genomic' : {}, "clinical" : {}, "probeMap" : {}, "sampleMap" : {} }
	
	def scanDirs(self, dirs):
		for dir in dirs:
			log("SCANNING DIR: %s" % (dir) )
			for path in glob( os.path.join( dir, "*.json" ) ):
				handle = open( path )
				data = json.loads( handle.read() )
				if data.has_key( 'name' ) and data['name'] is not None and data.has_key( 'type' ) and self.setHash.has_key( data['type'] ) :
					if self.setHash[ data['type'] ].has_key( data['name'] ):
						error( "Duplicate %s file %s" % ( data['type'], data['name'] ) )
					self.setHash[data['type'] ][ data['name'] ] = data
					self.pathHash[data['type'] ][ data['name'] ] = path
					log( "FOUND: " + data['type'] + "\t"+ data['name'] + "\t" + path )
				else:
					warn( "Unknown file type: %s" % ( path ) )
				handle.close()
				
	def validate(self):
		self.validate_1()
		self.validate_2()

	def validate_1(self):
		removeList = []
		for genomicName in self.setHash[ 'genomic' ]:
			genomicData = self.setHash[ 'genomic' ][ genomicName ]
			if genomicData[ 'probeMap' ] is None:
				error("%s lacks probeMap" % ( genomicName ) )
				removeList.append( genomicName )

			if genomicData[ 'sampleMap' ] is None:
				error("%s lacks sampleMap" % ( genomicName ) )
				removeList.append( genomicName )

			if self.setHash[ 'probeMap' ].has_key( genomicData[ 'probeMap' ] ):
				probeData = self.setHash[ 'probeMap' ][ genomicData[ 'probeMap' ] ]
				probeName = genomicData[ 'probeMap' ]
			else:
				error( "%s Missing Probe Data: %s" % ( genomicName, genomicData[ 'probeMap' ] ) )
				removeList.append( genomicName )
				
			if self.setHash[ 'sampleMap' ].has_key( genomicData[ 'sampleMap' ] ):
				sampleData = self.setHash[ 'sampleMap' ][ genomicData[ 'sampleMap' ] ]
				sampleName = genomicData[ 'sampleMap' ]
			else:
				error( "%s Missing Sample Data: %s" % ( genomicName, genomicData[ 'sampleMap' ] ) )	
				removeList.append( genomicName )

		print "Remove", removeList
		for remove in removeList:
			if remove in self.setHash[ 'genomic' ]:
				del self.setHash[ 'genomic' ][ remove ]

	def validate_2(self):
		removeList = []
		for genomicName in self.setHash[ 'genomic' ]:
			genomeInfo = self.setHash[ 'genomic' ][ genomicName ]
			probeInfo  = self.setHash[ 'probeMap'][ genomeInfo[ 'probeMap' ] ]			
			gPath = self.pathHash[ 'genomic' ][ genomicName ].replace(".json", "")
			gm = cgData.matrix.GeneMatrix()
			try:
				handle = open( gPath )
			except IOError:
				error( "unable to open matrix file %s" % ( gPath ) )
				removeList.append( genomicName )
				continue

			gm.readTSV( handle, skipVals=True )
			handle.close()

			sPath = self.pathHash[ 'probeMap' ][ genomeInfo[ 'probeMap' ] ].replace(".json", "")				
			sm = cgData.sampleMap.SampleMap()
			handle = open( sPath )
			sm.read( handle )
			handle.close()
			
			
			#print gm.getSampleList()
			
			
