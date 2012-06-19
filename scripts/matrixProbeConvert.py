#!/usr/bin/env python

import tempfile
import os
import csv
import CGData.GenomicMatrix
import CGData.AliasMap
import CGData.GeneMap

def aliasConvert(matrix, aliasMap, outPath):
    out = CGData.GeneMap.aliasRemap(matrix, aliasMap)
    handle = open(outPath, "w")
    out.write(handle)
    handle.close()

if __name__ == "__main__":
	mtx = CGData.GenomicMatrix()
    mtx.load(sys.argv[1])
    am = CGData.AliasMap()
    am.load(sys.argv[2])    
    aliasConvert(mtx, am, sys.argv[3])
        
