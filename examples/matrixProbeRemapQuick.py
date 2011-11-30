#!/usr/bin/env python

#note: this script assumes that the first alias in the probeMap aliaslist 
#is a HUGO gene name...

import CGData
import csv
import sys

# matrixProbeRemap.py <matrixFile> <probeFile>

#load the probeMap
probeMap = CGData.load( sys.argv[2] )


#remap the matrix using the probe map

remap = {}
for alt in probeMap.get_probes():
	remap[ alt.name ] = alt.aliases

handle = open(sys.argv[1])
read = csv.reader(handle, delimiter="\t")

oHandle = open(sys.argv[3], "w")
write = csv.writer(oHandle, delimiter="\t", lineterminator="\n")
head = None
for row in read:
	if head is None:
		head = row
		write.writerow(row)
	else:
		if row[0] in remap:
			for alt in remap[row[0]]:
				row[0] = alt
				write.writerow(row)
handle.close()
oHandle.close()	

#matrix.add_history( "Transformed from probespace %s to HUGO" % (probeMap.get_name() ) )
#matrix[":probeMap"] = "hugo"
#output the matrix
#matrix.store( sys.argv[3] )
