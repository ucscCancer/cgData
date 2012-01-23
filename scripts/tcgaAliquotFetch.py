#!/usr/bin/env python

import sys
import csv
import json
from urllib import urlopen
import datetime

url = "http://tcga-data.nci.nih.gov/datareports/aliquotIdBreakdownExport.htm?exportType=csv&cols=aliquotId,analyteId,sampleId,participantId"

if __name__ == "__main__":
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
        out.write( "%s\t%s\t%s\n" % (e["Participant ID"],e["Sample ID"], "sample"))
        out.write( "%s\t%s\t%s\n" % (e["Sample ID"], e["Analyte ID"], "analyte"))
        out.write( "%s\t%s\t%s\n" % (e["Analyte ID"], e["Aliquot ID"], "aliquot"))
    out.close()

    meta = {
        'cgdata': {
            'type' : 'idDAG',
            'name' : 'tcga.idDAG',
            'version' : datetime.date.today().isoformat() 
        }
    }

    out = open(sys.argv[1] + ".json", "w")
    out.write(json.dumps(meta))
    out.close()
