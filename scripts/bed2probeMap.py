#!/usr/bin/env python

import sys
import cgData.map
from getopt import getopt
import csv

opts, args = getopt( sys.argv[1:], "".join(cgData.map.optionMap.keys()) )


#hitFunc is the function that will be used to do the overlap comparision
hitFunc = cgData.map.geneOverlap
for a, o in opts:
	hitFunc = cgData.map.optionMap[ a[1:] ]

handle = open( args[0] )
mapper = cgData.map.ProbeMapper( handle )
handle.close()
handle = open( args[1] )
read = csv.reader( handle, delimiter="\t" )
line=1

for row in read:
	try:
		if len(row) == 12:
			out = mapper.findOverlap( row[0], row[5], int(row[1]), int(row[2]), hitFunc )
			o = []
			for e in out:
				o.append( str(e) )
			print "%s\t%s\t%s\t%s\t%s\t%s" % (row[3], ",".join(o), row[0], row[1], row[2], row[5] )
		else:
			sys.stderr.write("WARNING BADLINE: %d = %s\n" % (line,str(row)))
		
	except Exception, e:
		sys.stderr.write("WARNING LINE: %d = %s\n" % (line,str(e)))
	line += 1
