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


errorLogHandle = None
def error(eStr):
    sys.stderr.write("ERROR: %s\n" % (eStr) )
    errorLogHandle.write( "ERROR: %s\n" % (eStr) )

def warn(eStr):
    sys.stderr.write("WARNING: %s\n" % (eStr) )
    errorLogHandle.write( "WARNING: %s\n" % (eStr) )

def log(eStr):
    sys.stderr.write("LOG: %s\n" % (eStr) )
    errorLogHandle.write( "LOG: %s\n" % (eStr) )

includeList = None

if __name__ == "__main__":
    opts, args = getopt( sys.argv[1:], "p:" )
    params = {}
    for a,o in opts:
        if a == "-p":
			tmp = o.split("=")
			params[tmp[0]] = tmp[1]


    cg = CGData.Compiler.BrowserCompiler(params)
    cg.scan_dirs( args )
    
    cg.link_objects()
    cg.build_ids()
    cg.gen_sql()

