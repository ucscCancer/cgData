#!/usr/bin/env python

import sys
import csv
import json
from urllib import urlopen
import datetime

url = "http://tcga-data.nci.nih.gov/datareports/aliquotIdBreakdownExport.htm?exportType=csv&cols=aliquotId,analyteId,sampleId,participantId"

handle = urlopen(url)
reader = csv.reader(handle)

data = []
head = None
for row in reader:
	if head is None:
		head = {}
		for c in row:
			head[c] = len(head)
		print head
	else:
		d = {}
		for i in head:
			d[i] = row[head[i]]
		data.append(d)
handle.close()


out = open( sys.argv[1], "w")
for e in data:
	out.write( "%s\t%s\n" % (e["Participant ID"],e["Sample ID"]))
	out.write( "%s\t%s\n" % (e["Sample ID"], e["Analyte ID"]))
	out.write( "%s\t%s\n" % (e["Analyte ID"], e["Aliquot ID"]))
out.close()

meta = {
	'type' : 'sampleMap',
	'name' : 'tcga',
	'timestamp' : datetime.date.today().isoformat() 
}

out = open(sys.argv[1] + ".json", "w")
out.write(json.dumps(meta))
out.close()
