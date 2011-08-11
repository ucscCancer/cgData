#!/usr/bin/env python

import sys
import cgData.gaf
import cgData.probeMap

#open a gaf file and use it to create a probeMap file

handle = open( sys.argv[1] )
g = cgData.gaf.gaf()
g.read( handle, strict=False )

s = cgData.probeMap.probeMap()

for a in g:
    if a.compositeType == 'gene':
        try:
            s.append( a )
        except cgData.formatException:
            pass

s.write( sys.stdout )
