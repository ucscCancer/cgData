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
from getopt import gnu_getopt
reJson = re.compile( r'.json$' )

if __name__ == "__main__":
    opts, args = gnu_getopt( sys.argv[1:]
                         ,"bp:f:vt:hd:", ["no-g","no-gc","save-ds","help"] )

    params = {}
    params['binary'] = False

    # top-level objects that should be processed
    trackTypes = set(['trackGenomic', 'trackClinical'])
    # compiler options
    copts = {}
    copts['types'] = trackTypes

    for a,o in opts:
        if a =="-h" or a=="--help":
            print "options:"
            print "        --no-g (skip genomic matrix)"
            print "        --no-gc (skip genomic and clinical matrix)"
            print "        --save-ds (save downsample table in raDb)"
            sys.exit()

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
        if a =="--save-ds":
            copts['save-ds'] = True
        if a =="--no-g":
            copts['no-genomic-matrix'] = True
        if a =="--no-gc":
            trackTypes.remove('trackClinical')
            copts['no-genomic-matrix'] = True


    ds = CGData.DataSet.DataSet(params)
    ds.scan_dirs(args)
    cg = CGData.Compiler.BrowserCompiler(ds, params)
    cg.link_objects()
    cg.gen_sql("heatmap", copts)

