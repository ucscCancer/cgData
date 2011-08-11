#!/usr/bin/env python

#use a sample map to check for sample overlaps between matrix files

import sys
from cgData.matrix import GeneMatrix
from cgData.sampleMap import SampleMap

handle = open( sys.argv[1] )
sm = SampleMap()
sm.read( handle )
handle.close()

gmList = []
sampleHash = {}
for path in sys.argv[2:]:
    gm = GeneMatrix()
    handle = open( path )
    gm.readTSV( handle, skipVals=True )
    handle.close()
    gmList.append( gm )
    for sample in gm.getSampleList():
        if sample not in sampleHash:
            sampleHash[ sample ] = []
        sampleHash[ sample ].append( path )

sampleRemap = {}
for sample in sampleHash:
    children = sm.getChildren( sample ) 
    for c in children:
        if c in sampleHash:
            sampleRemap[ c ] = sample

test = {}
for v in sampleRemap.values():
    test[v] = True

if len( test ) != len( sampleRemap ):
    print "WARNING Merging child remap"

for path in sys.argv[2:]:
    gm = GeneMatrix()
    handle = open( path )
    gm.readTSV( handle )
    handle.close()
    for sample in sampleRemap:
        gm.sampleRename( sample, sampleRemap[ sample ] )    
    oHandle = open( path + ".remap", "w" )
    gm.writeTSV( oHandle )
    oHandle.close()
    

