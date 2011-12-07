#!/usr/bin/env python

import CGData.ORM
import sys
from numpy import *
import csv

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
	"""
	This class takes arrays that are named via associated index maps
	(ie to access value named 'my_val': array[ name_map['my_val'] ])
	and reorders arrays to a common ordering, so that you can do 
	vector based math on them
	"""
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

#scan the genomic matrices for dataSubType 'geneExp',
#and determine how many samples will be involved altogeather
for name in orm['genomicMatrix']:
	data = orm['genomicMatrix'][name]
	if data[":dataSubType"] == "geneExp":
		dataset[name] = data
		for col in data.get_col_list():
			sampleName = name + ":" + col 
			sampleMap[ sampleName ] = len(sampleMap)
		for row in data.get_row_list():
			organizer.add_name(row)

def med_normalize(vec):
	med = median(vec,0)
	return (vec - med) / std(vec)
	

#scan through the selected matrices 
datasetNames = dataset.keys()
for i in range(len(datasetNames)):
	name_i = datasetNames[i]
	dataset_i = dataset[ name_i ]
	sample_set_i = {}
	for col_i in dataset_i.get_col_list():
		sample_i = med_normalize( nan_to_num( organizer.transform( dataset_i.get_row_map(), dataset_i.get_col(col_i) ) ) )
		sample_set_i[ name_i + ":" + col_i ] = sample_i

	for j in range(i,len(datasetNames)):		
		name_j = datasetNames[j]
		dataset_j = dataset[ name_j ]	
		sample_set_j = {}
		for col_j in dataset_j.get_col_list():
			sample_j = med_normalize( nan_to_num( organizer.transform( dataset_j.get_row_map(), dataset_j.get_col(col_j) ) ) )
			sample_set_j[ name_j + ":" + col_j ] = sample_j
		
		#for the current pair of matrices, look at every column(sample) and 
		#calulate the euclidean distance
		print "calc", name_i, name_j
		for sample_i in sample_set_i:
			for sample_j in sample_set_j:
				value = sqrt(sum(( sample_set_i[sample_i]-sample_set_j[sample_j])**2))
				oMatrix[ sampleMap[ sample_i ] ][ sampleMap[ sample_j ] ] = value
				oMatrix[ sampleMap[ sample_j ] ][ sampleMap[ sample_i ] ] = value

sampleList = sampleMap.keys()
sampleList.sort( lambda x,y: sampleMap[x]-sampleMap[y])
handle = open( "test", "w" )
writer = csv.writer(handle, delimiter="\t", lineterminator='\n')
writer.writerow(["#"] + sampleList)
for sample in sampleList:
	row = ["NA"] * len(sampleMap)
	for i in sampleMap:
		row[sampleMap[i]] = str(oMatrix[sampleMap[sample]][sampleMap[i]])
	writer.writerow([sample] + row)
handle.close()

				
