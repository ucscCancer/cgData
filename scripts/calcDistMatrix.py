#!/usr/bin/env python

import CGData.ORM
import sys
from numpy import *

"""
This script scans a ORM repo and calculates a distance matrix 
representing the euclidian distance between all samples of the
'geneExpression' subtype
"""

orm = CGData.ORM.ORM(sys.argv[1])

sampleCount = 0
for name in orm['genomicMatrix']:
	data = orm['genomicMatrix'][name]
	if data[":dataSubType"] == "geneExp":
		sampleCount += data.get_col_count()

oMatrix = empty( (sampleCount, sampleCount) )
oMatrix.fill(0)

sampleMap = {}

dataset = {}

class NamedVectorOrganize:
	def __init__(self):
		self.name_map = {}
	
	def add_name(self,name):
		if name not in self.name_map:
			self.name_map[name] = len(self.name_map)
	
	def transform(self, name_map, vector):
		out = empty(len(self.name_map), 'f')
		out.fill(nan)
		for name in name_map:
			out[ self.name_map[name] ] = vector[ name_map[name] ]
		return out

organizer = NamedVectorOrganize()

for name in orm['genomicMatrix']:
	data = orm['genomicMatrix'][name]
	if data[":dataSubType"] == "geneExp":
		dataset[name] = data
		for col in data.get_col_list():
			sampleName = name + ":" + col 
			sampleMap[ sampleName ] = len(sampleMap)
		for row in data.get_row_list():
			organizer.add_name(row)

datasetNames = dataset.keys()

for i in range(len(datasetNames)):
	name_i = datasetNames[i]
	for j in range(i+1,len(datasetNames)):		
		name_j = datasetNames[j]
		dataset_i = dataset[ name_i ]
		dataset_j = dataset[ name_j ]		
		print "calc", name_i, name_j
		for col_i in dataset_i.get_col_list():
			sample_i = organizer.transform( dataset_i.get_row_map(), dataset_i.get_col(col_i) )
			probe_i = name_i + ":" + col_i
			for col_j in dataset_j.get_col_list():
				probe_j = name_j + ":" + col_j
				sample_j = organizer.transform( dataset_j.get_row_map(), dataset_j.get_col(col_j) )
				
				value = sqrt(sum((sample_i-sample_j)**2))
				
				oMatrix[ sampleMap[ probe_i ] ][ sampleMap[ probe_j ] ] = value
				oMatrix[ sampleMap[ probe_i ] ][ sampleMap[ probe_j ] ] = value
				
print oMatrix

