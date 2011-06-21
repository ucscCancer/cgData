import csv

class GeneMatrix:
	def __init__(self):
		self.probeHash = {}	
		self.sampleList = []
		self.attrs = {}

	def readTSV(self, handle ):
		self.sampleList = []
		self.probeHash = {}	
		posHash = None
		for row in csv.reader( handle, delimiter="\t" ):
			if posHash is None:
				posHash = {}
				pos = 1
				for name in row[1:]:
					i = 1
					origName = name
					while posHash.has_key( name ):
						name = origName + "#" + str(i)
						i += 1
					posHash[ name ] = pos
					pos += 1
			else:
				self.probeHash[ row[0] ] = {}
				if not skipVals:
					for sample in posHash:
						i = posHash[ sample ]
						if row[i] != 'NA' and row[i] != 'null' and len(row[i]):
							self.probeHash[ row[0] ][ sample ] = float(row[i])
		
		self.sampleList = posHash.keys()
		self.sampleList.sort( lambda x,y: posHash[x] - posHash[y] )
	
	def writeTSV(self, handle, missing='NA'):
		write = csv.writer( handle, delimiter="\t", lineterminator='\n' )
		write.writerow( [ "probe" ] + self.sampleList )
		for probe in self.probeHash:
			out = [ probe ]
			for sample in self.sampleList:
				out.append( self.probeHash[ probe ].get( sample, missing ) )
			write.writerow( out )

	def getProbeList(self):
		return self.probeHash.keys()

	def getSampleList(self):
		return self.sampleList
		
	
	def writeGCT(self, handle, missing=''):
		write = csv.writer( handle, delimiter="\t", lineterminator='\n' )
		write.writerow( ["#1.2"] )
		write.writerow( [ len(self.probeHash), len(self.sampleList) ] )
		write.writerow( [ "NAME", "Description" ] + self.sampleList )
		for probe in self.probeHash:
			out = [ probe, probe ]
			for sample in self.sampleList:
				out.append( self.probeHash[ probe ].get( sample, missing ) )
			write.writerow( out )

	def add( self, probe, sample, value ):
		if not self.probeHash.has_key( probe ):
			self.probeHash[ probe ] = {}
		if not sample in self.sampleList:
			self.sampleList.append( sample )
		self.probeHash[ probe ][ sample ] = value

