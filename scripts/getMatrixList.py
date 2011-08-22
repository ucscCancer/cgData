#!/usr/bin/env python

import sys
import CGData.Compiler

namespace = sys.argv[1]

cg = CGData.Compiler.BrowserCompiler()
cg.scan_dirs( sys.argv[2:] )

colNames = {}
 
for cName in cg[ namespace ]:
    cObj = cg[ namespace ][ cName ]
    for attr in cObj.attrs:
        if attr not in colNames:
            colNames[ attr ] = len( colNames )

row = [""] * len( colNames )
for col in colNames:
    row[ colNames[col] ] = col

print "name\t%s" % ("\t".join(row))

for cName in cg[ namespace ]:
    cObj = cg[ namespace ][ cName ]
    row = [""] * len( colNames )
    for col in colNames:
        row[ colNames[col] ] = str( cObj.attrs.get(col,"") or "" )
    print "%s\t%s" % (cName, "\t".join(row))
    
        



