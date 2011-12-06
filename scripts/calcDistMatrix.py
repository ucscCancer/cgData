#!/usr/bin/env python

import CGData.ORM
import sys

orm = CGData.ORM.ORM(sys.argv[1])

for type in orm:
	print type

sampleCount = 0
for name in orm['genomicMatrix']:
	data = orm[type][name]
	if data[":dataSubType"] == "geneExp":
		sampleCount += data.get_col_count()

matrix = numpy.matrix( (sampleCount, sampleCount) )
print sampleCount
