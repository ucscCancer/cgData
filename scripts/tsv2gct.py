#!/usr/bin/env python

from cgData.matrix import GeneMatrix
import sys


handle = open( sys.argv[1] )

gm = GeneMatrix()
gm.readTSV( handle )

gm.writeGCT( sys.stdout, missing="0" )
