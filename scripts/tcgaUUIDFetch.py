#!/usr/bin/env python

import sys
import urllib
import json

url = "https://tcga-data.nci.nih.gov/uuid/uuidBrowser.json"
query = """{"uuidSearchRadio":true,"uuidField":"","barcodeSearchRadio":false,"barcodeField":"","fileSearchRadio":false,"file":""}"""


if __name__ == "__main__":
	
	totalCount = None
	offset = 0
	step = 1000
	while totalCount is None or offset < totalCount:
		data = json.loads( urllib.urlopen( url, urllib.urlencode( {"start" : offset, "limit" : step, "searchParams" : query} ) ).read() )
		for a in data['uuidBrowserData']:
			if totalCount is None:
				totalCount = data['totalCount']
			print "%s\t%s\t%s\t%s" % (a['barcode'], a['uuid'], a.get('parentUUID', ""), a['disease'])
				
		offset += step
			
