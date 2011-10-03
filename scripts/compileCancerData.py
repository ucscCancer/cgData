#!/usr/bin/env python

import os
import sys
from glob import glob
import json
import re
import CGData
import CGData.Compiler
import CGData.DataSet

import csv
from getopt import getopt
reJson = re.compile( r'.json$' )

OUT_DIR = "genRA"
DATABASE_NAME = "hg18_test"

includeList = None

if __name__ == "__main__":
    opts, args = getopt( sys.argv[1:], "bp:f:v" )
    params = {}
    params['binary'] = False
    for a,o in opts:
        if a == "-p":
            tmp = o.split("=")
            params[tmp[0]] = tmp[1]
        if a == "-f":
            params["filter"] = {}
            tmp = o.split(",")
            for p in tmp:
                tmp2 = p.split("=")
                params["filter"][tmp2[0]] = tmp2[1]
        if a == "-v":
            CGData.LOG_LEVEL = 0
        if a == "-b":
            params['binary'] = True
            
    ds = CGData.DataSet.DataSet(params)
    ds.scan_dirs(args)
    cg = CGData.Compiler.BrowserCompiler(ds, params)
    cg.link_objects()
    cg.gen_sql()

