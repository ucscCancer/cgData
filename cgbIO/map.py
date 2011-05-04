#!/usr/bin/env python

import csv
import sys
import re

#column definitions for the current refGene_hg18.table
COL_CHROME  =2
COL_STRAND  =3
COL_START   =4
COL_END     =5
COL_EXCOUNT =8
COL_EXSTART =9
COL_EXEND   =10
COL_HUGO    =12

#sometimes the ref table ends with a comma, which makes 
#arrays that end with '' when you split
reCommaEnd = re.compile( r',$' )

class geneInfo:
	"""
	Class to hold information about gene, including exon start/stops
	"""
	def __init__(self, chrom, strand, start, end, exCount, exStart, exEnd, hugo):
		self.chrom = chrom
		self.strand = strand
		self.start = int(start)
		self.end = int(end)
		self.exCount = exCount
		self.exStart = []
		for p in reCommaEnd.sub("", exStart).split(','):
			self.exStart.append( int(p) )
		self.exEnd = []
		for p in reCommaEnd.sub("",exEnd).split(','):
			self.exEnd.append( int(p) )
		self.hugo = hugo

	def __repr__(self):
		#return "%s_%s_%d_%d" % (self.hugo, self.chrom,  self.start, self.end )
		return self.hugo
		
		
class ProbeMapper:
	"""
	Class to map the probes. Expects handle to the refGene_hg18.table file 
	"""
	def __init__(self, handle):
		read = csv.reader( handle, delimiter="\t")

		self.hugoMap = {}
		for row in read:
			gene = geneInfo( row[COL_CHROME],
				row[COL_STRAND],
				row[COL_START], 
				row[COL_END], 
				row[COL_EXCOUNT],  
				row[COL_EXSTART],  
				row[COL_EXEND], 
				row[COL_HUGO] )
			self.hugoMap[ row[COL_HUGO] ] = gene
		
		
		self.chromeMap = {}
		for hugo in self.hugoMap:
			if not self.chromeMap.has_key( self.hugoMap[ hugo ].chrom ):
				self.chromeMap[ self.hugoMap[ hugo ].chrom ] = []
			self.chromeMap[ self.hugoMap[ hugo ].chrom ].append( self.hugoMap[ hugo ] )
		
		for chrom in self.chromeMap:
			self.chromeMap[ chrom ].sort( lambda x,y : x.start - y.start )

	def findOverlap( self, chrome, strand, start, end, cmpFunc ):
		"""
		Function to find overlaps for a given probe description.
		the cmpFunc arg is a function that returns a 'True' or 'False' for
		a given probe description and a gene, examples include 'geneOverlap' and 
		'geneSimpleMethOverlap'
		"""
		if not self.chromeMap.has_key( chrome ):
			return []
		chromeList = self.chromeMap[ chrome ]
		startDist = abs( self.chromeMap[ chrome ][0].start - start )
		endDist   = abs( self.chromeMap[ chrome ][-1].end - end )
		
		out = []
		for gene in self.chromeMap[ chrome ]:
			if cmpFunc( start, end, strand, gene ):
				out.append( gene )
		return out


#
# The set of functions that can be used to do comparisons
#
def geneOverlap( start, end, strand, gene ):
	if gene.strand == gene.strand and gene.end > start and gene.start < end:
		return True
	return False

def geneSimpleMethOverlap( start, end, strand, gene ):
	if gene.end > start and gene.start < end:
		return True
	return False

###ADD MORE FUNCTIONS HERE


####

###To add options to the command line, map the option character to a function
###for example '-m' maps to geneSimpleMethOverlap

optionMap = {
	"m" : geneSimpleMethOverlap
}


if __name__ == '__main__':
	from getopt import getopt
	
	opts, args = getopt( sys.argv[1:], "".join(optionMap.keys()) )
	
	#hitFunc is the function that will be used to do the overlap comparision
	hitFunc = geneOverlap
	for a, o in opts:
		hitFunc = optionMap[ a[1:] ]
	
	handle = open( args[0] )
	mapper = ProbeMapper( handle )
	handle.close()
	handle = open( args[1] )
	read = csv.reader( handle, delimiter="\t" )
	for row in read:
		#this example column input is in the bed12 column order
		out = mapper.findOverlap( row[0], row[5], int(row[1]), int(row[2]), hitFunc )
		if len(out):
			print row[3], out
