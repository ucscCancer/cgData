#!/usr/bin/env python

"""

Script to fetch idDAG description of tcga ids from the DCC servers

usage::
    ./tcgaIDDagFetch.py <outfileName>

"""

import sys
import csv
import json
from urllib import urlopen
import datetime

url = "http://tcga-data.nci.nih.gov/datareports/aliquotIdBreakdownExport.htm?exportType=csv&cols=aliquotId,analyteId,sampleId,participantId"

def write_tcgaIDDag(dst):
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


    out = open( dst, "w")
    for e in data:
        vialID = e["Sample ID"] + e["Vial ID"]
        out.write( "%s\t%s\n" % (e["Participant ID"],e["Sample ID"]))
        out.write( "%s\t%s\n" % (e["Sample ID"], vialID))
        out.write( "%s\t%s\n" % (vialID, e["Analyte ID"]))
        out.write( "%s\t%s\n" % (e["Analyte ID"], e["Aliquot ID"]))
    out.close()

    meta = {
        'cgdata': {
            'type' : 'idDAG',
            'name' : 'tcga.idDAG',
            'version' : datetime.date.today().isoformat() 
        }
    }

    out = open(dst + ".json", "w")
    out.write(json.dumps(meta))
    out.close()


if __name__ == "__main__":
    write_tcgaIDDag(sys.argv[1])
