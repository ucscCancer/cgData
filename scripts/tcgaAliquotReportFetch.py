#!/usr/bin/env python

import sys
import csv
import json
from urllib import urlopen
import datetime

url = "http://tcga-data.nci.nih.gov/datareports/aliquotExport.htm?exportType=csv&dir=undefined&sort=undefined&cols=aliquotId,disease,bcrBatch,center,platform,levelOne,levelTwo,levelThree"

handle = urlopen(url)
reader = csv.reader(handle)

ohandle = open(sys.argv[1], "w")
writer = csv.writer( ohandle, delimiter="\t", lineterminator='\n' )

data = []
head = None
for row in reader:
	writer.writerow(row)
handle.close()
ohandle.close()

meta = {
	'cgdata': {
		'type' : 'clinicalMatrix',
		'name' : 'tcga.aliquotReport',
		'version' : datetime.date.today().isoformat(),
		'rowKeySrc' : {
			'type' : 'idDAG',
			'name' : 'tcga'			
		}
	}
}

out = open(sys.argv[1] + ".json", "w")
out.write(json.dumps(meta))
out.close()
