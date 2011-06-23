

class SampleMap:
	def __init__(self):
		self.sampleHash = {}
	
	def read(self, handle):
		for line in handle:
			tmp = line.rstrip().split('\t')			
			if not tmp[0] in self.sampleHash:
				self.sampleHash[ tmp[0] ] = {}			
			if len(tmp) > 1:
				self.sampleHash[ tmp[0] ][ tmp[1] ] = True
				
	def getChildren(self, sample):
		out = {}
		for a in self.sampleHash.get( sample, {} ):
			out[ a ] = True
			for c in self.getChildren( a ):
				out[ c ] = True
		return out.keys()
