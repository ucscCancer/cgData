#!/usr/bin/env python

import sys
from getopt import getopt

import CGData.ORM
import CGData.DataSet
import CGData.HeatMapCompiler



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

    #orm = CGData.ORM.ORM(args[0])
    
    orm = CGData.DataSet.DataSet()
    orm.scan_dirs( [args[0]])
    
    cg = CGData.HeatMapCompiler.BrowserCompiler(orm, params)
    
    cg.gen_sql()
