#!/usr/bin/env python

import sys
import json
import csv


path = sys.argv[1]
handle = open( path + ".json" )
meta = json.loads( handle.read() )
handle.close()



meta['cgdata'] =  { 'type' : 'genomicMatrix', 'name' : meta['dataset_id'][0] }
meta['cgdata']['columnKeyMap'] = { 'type' : 'id', 'name' : 'geo' }
meta['cgdata']['rowKeyMap'] = { 'type' : 'probe', 'name' : 'geo.' + meta['platform']  }

ohandle = open( path + ".cgdata.json", "w" )
ohandle.write(json.dumps(meta))
ohandle.close()

ihandle = open( path )
reader = csv.reader(ihandle, delimiter="\t")
ohandle = open( path + ".cgdata", "w" )
writer = csv.writer( ohandle, delimiter="\t", lineterminator="\n")
for row in reader:
	writer.writerow( [row[0]] + row[2:] )
ohandle.close()
ihandle.close()
