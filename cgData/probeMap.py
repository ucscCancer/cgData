
import csv
import json

class ProbeMap:

	def __init__(self):
		self.geneMap = {}
		self.chromeMap = {}
	
	def readMeta( self, handle ):
		self.attrs = json.loads( handle.read () )
	
	def read(self, handle):
		read = csv.reader( handle, delimiter="\t" )
		for line in read:
			self.geneMap[ line[0] ] = line[1].split(',')
			self.chromeMap[ line[0] ] = ( line[2], int(line[3]), int(line[4]), line[5] )
