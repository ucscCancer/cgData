#!/usr/bin/env python

import os
import sys
from glob import glob
import json
import re
import CGData
import CGData.DataSet
import CGData.ORM

import csv
from getopt import getopt

includeList = None

if __name__ == "__main__":
    opts, args = getopt( sys.argv[1:], "bp:f:vo:s" )
    params = {}
    outFile = "test"
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
        if a == "-o":
            outFile = o
        if a == "-s":
            params['storeMatrix'] = False
            
    ds = CGData.DataSet.DataSet()
    ds.scan_dirs(args)
    sess = CGData.ORM.ORM(outFile, params)
    for t in ds:
        for name in ds[t]:
            print "Scanning ", t, name 
            try:
                if not sess.loaded( ds[t][name].path, md5Check=False ):
                    print "Storing ", t, name 
                    sess.write( ds[t][name] )
                ds[t][name].unload()
            except IOError as e:
                print e
    sess.commit()
