#!/usr/bin/env python

import sys
import csv
import CGData.Compiler

editHash={}

handle = open( sys.argv[1] )
reader = csv.reader(handle)

rowNum = None

for row in reader:
    if rowNum is None:
        rowNum = {}
        for i in range(1,len(row)):
            rowNum[ i ] = row[i]
    else:
        e = {}
        for i in range(1,len(row)):
            e[ rowNum[i] ] = row[i]
        editHash[ row[0] ] = e
handle.close()

editSpace = sys.argv[2]

print editHash

cg = CGData.Compiler.BrowserCompiler()
cg.scan_dirs( sys.argv[3:] )

for cName in cg[ editSpace ]:
    if cName in editHash:
        cObj = cg[ editSpace ][ cName ]
        for col in editHash[ cName ]:
            if len(editHash[ cName ][col]):
                cObj.attrs[col] = editHash[ cName ][col]
            else:
                if col in cObj.attrs:
                    del cObj.attrs[col]
        print cObj.attrs
        cObj.store()
