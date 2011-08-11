#!/usr/bin/env python

import sys
import csv
import cgData.compiler

editHash={}

handle = open( sys.argv[1] )
reader = csv.reader( handle, delimiter="\t" )

rowNum = None

for row in reader:
    if rowNum is None:
        rowNum = {}
        for i in range(1,len(row)):
            rowNum[ i ] = row[i]
    else:
        e = {}
        for i in rowNum:
            e[ rowNum[i] ] = row[i]
        editHash[ row[0] ] = e
handle.close()

print editHash

cg = cgData.compiler.browserCompiler()
cg.scanDirs( sys.argv[2:] )

for cName in cg[ 'genomicMatrix' ]:
    if cName in editHash:
        cObj = cg[ 'genomicMatrix' ][ cName ]
        for col in editHash[ cName ]:
            cObj.attrs[col] = editHash[ cName ][col]
            print cObj.attrs
            cObj.store()
