#!/usr/bin/env python

import sys
import cgData.compiler



cg = cgData.compiler.browserCompiler()
cg.scanDirs( sys.argv[2:] )


colNames = {}
 
for cName in cg[ 'genomicMatrix' ]:
    cObj = cg[ 'genomicMatrix' ][ cName ]
    for attr in cObj.attrs:
        if attr not in colNames:
            colNames[ attr ] = len( colNames )

row = [""] * len( colNames )
for col in colNames:
    row[ colNames[col] ] = col

print "name\t%s" % ("\t".join(row))

for cName in cg[ 'genomicMatrix' ]:
    cObj = cg[ 'genomicMatrix' ][ cName ]
    row = [""] * len( colNames )
    for col in colNames:
        row[ colNames[col] ] = str( cObj.attrs.get(col,"") or "" )
    print "%s\t%s" % (cName, "\t".join(row))
    
        



