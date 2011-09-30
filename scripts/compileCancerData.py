#!/usr/bin/env python

import os
import sys
from glob import glob
import json
import re
import CGData
import CGData.Compiler

import csv
from getopt import getopt
reJson = re.compile( r'.json$' )

OUT_DIR = "genRA"
DATABASE_NAME = "hg18_test"

includeList = None

if __name__ == "__main__":
    opts, args = getopt( sys.argv[1:], "d:l:v" )
    for a,o in opts:
        if a == "-l":
            handle = open( o )
            includeList = {}
            for line in handle:
                includeList[ line.rstrip() ] = True
            handle.close()
        if a == "-d":
            DATABASE_NAME = o
        if a == "-v":
            CGData.LOG_LEVEL = 0


    cg = CGData.Compiler.BrowserCompiler()
    cg.scan_dirs( args )
    
    cg.link_objects()
    cg.build_ids()
    cg.gen_sql()

