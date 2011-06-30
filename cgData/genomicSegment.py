
import cgData

class Segment:
	def __init__(self, chrome, start, end, strand, value ):
		self.chrome = chrome.lower()
		if not self.chrome.startswith('chr'):
			self.chrome = 'chr' + self.chrome
		self.start = start
		self.end = end
		self.strand = strand
		self.value = value	 

class genomicSegment( cgData.baseObject ) :
	def __init__(self):
		self.sampleHash = {}
	
	def read( self, handle ):
		self.sampleHash = {}
		for line in handle:
			tmp = line.rstrip().split( "\t" )			
			if not self.sampleHash.has_key( tmp[0] ):
				self.sampleHash[ tmp[0] ] = []			
			self.sampleHash[ tmp[0] ].append( Segment(tmp[1], int(tmp[2]), int(tmp[3]), tmp[4], float(tmp[5]) ) )

	def __iter__(self):
		for key in self.sampleHash:
			yield key

	def __getitem__(self, i):
		return self.sampleHash[ i ]
