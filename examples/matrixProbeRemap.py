#!/usr/bin/env python


import cgData
import sys

# matrixProbeRemap.py <matrixFile> <probeFile>

#load the matrix
matrix = cgData.load( sys.argv[1] )

#load the probeMap
probeMap = cgData.load( sys.argv[2] )

#remove null probes from the matrix
matrix.removeNullProbes()

#remap the matrix using the probe map
matrix.remap( probeMap, skipMissing=True )

matrix.addHistory( "Transformed from probespace %s to HUGO" % (probeMap.getName() ) )

#output the matrix
matrix.store( sys.argv[1] + ".hugo" )
