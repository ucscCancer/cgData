#!/usr/bin/env python

import sys
import cgData.segToMatrix


handle = open( sys.argv[1] )
oHandle = sys.stdout

cgData.segToMatrix.segToMatrix( handle, oHandle )

