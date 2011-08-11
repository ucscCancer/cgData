#!/usr/bin/env python

import sys
import cgData.compile
from glob import glob

dirs  =[]
for dir in sys.argv[1:]:
    dirs.extend( glob( dir ) )

comp = cgData.compile.BrowserCompile()

comp.scanDirs( dirs )

comp.validate()
