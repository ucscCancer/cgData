#!/usr/bin/env python

import csv
import sys
import re

		
class ProbeMapper:
	"""
	Class to map the probes. Expects handle to the refGene_hg18.table file 
	"""
	def __init__(self, mode='g'):
		self.cmpFunc = optionMap[ mode ]
		
	def findOverlap( self, segment, refGene, cmpFunc=None ):
		"""
		Function to find overlaps for a given probe description.
		the cmpFunc arg is a function that returns a 'True' or 'False' for
		a given probe description and a gene, examples include 'geneOverlap' and 
		'geneSimpleMethOverlap'
		"""
		if cmpFunc is None:
			cmpFunc = self.cmpFunc
		if not refGene.hasChrome( segment.chrome ):
			return []
		chromeList = refGene.getChrome( segment.chrome )
	
		out = []
		for gene in chromeList:
			if cmpFunc( segment.start, segment.end, segment.strand, gene ):
				out.append( gene )
		return out


#
# The set of functions that can be used to do comparisons
#
def geneOverlap( start, end, strand, gene ):
	if gene.strand == gene.strand and gene.end > start and gene.start < end:
		return True
	return False

def blockOverlap( start, end, strand, gene ):
	if gene.end > start and gene.start < end:
		return True
	return False
	
def exonOverlap( start, end, strand, gene ):
	if gene.strand != gene.strand:
		return False
	for i in range( gene.exCount ):
		if gene.exEnd[i] > start and gene.exStart[i] < end:
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
	"g" : geneOverlap,
	"b" : blockOverlap,
	"m" : geneSimpleMethOverlap,
	"e" : exonOverlap
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
