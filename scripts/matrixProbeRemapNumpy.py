#!/usr/bin/env python

#note: this script assumes that the first alias in the probeMap aliaslist 
#is a HUGO gene name...

import CGData
import CGData.NumpyMatrix
import sys

# matrixProbeRemap.py <matrixFile> <probeFile>

#load the matrix


matrix = CGData.NumpyMatrix.NumpyMatrix()
matrixHandle = open(sys.argv[1])
matrix.read(matrixHandle)
matrixHandle.close()

#load the probeMap
probeMap = CGData.load( sys.argv[2] )

#remove null probes from the matrix
matrix.remove_null_probes()

#remap the matrix using the probe map

valid_map = {}
for alt in probeMap.get_probes():
	valid_map[alt.aliases[0]] = True
	if alt.name in matrix.get_row_names():
		matrix.row_rename(alt.name, alt.aliases[0])

remove_list = []
for name in matrix.get_row_names():
	if not name in valid_map:
		remove_list.append(name)
#for name in remove_list:
#	matrix.row_remove(name)
matrix.row_remove(remove_list)

matrix.add_history( "Transformed from probespace %s to HUGO" % (probeMap.get_name() ) )
matrix[":probeMap"] = "hugo"
#output the matrix
matrix.store( sys.argv[3] )
