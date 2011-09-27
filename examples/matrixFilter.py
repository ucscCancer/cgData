#!/usr/bin/env python

from CGData.TSVMatrix import TSVMatrix
import sys
from getopt import getopt

opts, args = getopt(sys.argv[1:], "r:c:")

handle = open(args[0])
t = TSVMatrix()
t.read(handle)
handle.close()

for o,a in opts:
	if o == "-c":
		for n in a.split(","):
			t.del_col( n )

	if o == "-r":
		for n in a.split(","):
			t.del_row( n )


t.write( sys.stdout )