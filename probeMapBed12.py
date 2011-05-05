#!/usr/bin/env python

import sys
import cgbIO.map
from getopt import getopt
import csv

opts, args = getopt( sys.argv[1:], "".join(cgbIO.map.optionMap.keys()) )


#hitFunc is the function that will be used to do the overlap comparision
hitFunc = cgbIO.map.geneOverlap
for a, o in opts:
	hitFunc = cgbIO.map.optionMap[ a[1:] ]

handle = open( args[0] )
mapper = cgbIO.map.ProbeMapper( handle )
handle.close()
handle = open( args[1] )
read = csv.reader( handle, delimiter="\t" )
for row in read:
	#this example column input is in the bed12 column order
	out = mapper.findOverlap( row[0], row[5], int(row[1]), int(row[2]), hitFunc )
	if len(out):
		o = []
		for e in out:
			o.append( str(e) )
		print "%s\t%s" % ("\t".join(row), ",".join(o) )
