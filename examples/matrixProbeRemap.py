#!/usr/bin/env python

#note: this script assumes that the first alias in the probeMap aliaslist 
#is a HUGO gene name...

import CGData
import sys

# matrixProbeRemap.py <matrixFile> <probeFile>

#load the matrix
matrix = CGData.load( sys.argv[1] )

#load the probeMap
probeMap = CGData.load( sys.argv[2] )

#remove null probes from the matrix
matrix.remove_null_probes()

#remap the matrix using the probe map
matrix.remap( probeMap, skip_missing=True )

matrix.add_history( "Transformed from probespace %s to HUGO" % (probeMap.get_name() ) )
matrix.attrs[":probeMap"] = "hugo"
#output the matrix
matrix.store( sys.argv[3] )
