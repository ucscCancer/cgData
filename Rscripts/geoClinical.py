#!/usr/bin/env python

import json
import sys
import os
from StringIO import StringIO
from xml.etree.ElementTree import parse


import Bio.Entrez

Bio.Entrez.email = "kellrott@soe.ucsc.edu"

path = sys.argv[1]
handle = open( path + ".json" )
meta = json.loads( handle.read() )
handle.close()

print meta['pubmed_id']

handle = Bio.Entrez.efetch(db="pubmed", id=meta['pubmed_id'], retmode="xml", rettype="abstract")

xml = handle.read()

tree = parse(StringIO(xml))

abstract = None
for e in tree.findall(".//AbstractText"):
	abstract = e.text

ometa = { "cgdata" : { "name" : "pubmed." + meta['pubmed_id'], "type" : "pubmedAbstract" } }

opath = os.path.join( sys.argv[2], "pubmedAbstract." + meta['pubmed_id'] )
ohandle = open( opath, "w" )
ohandle.write(abstract)

mhandle = open( opath + ".json", "w")
mhandle.write( json.dumps(ometa) )
mhandle.close()
