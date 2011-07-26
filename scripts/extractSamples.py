#!/usr/bin/env python

import MySQLdb
import _mysql_exceptions
import sys
import json
import csv
import re
import os

serverList = json.loads( open( sys.argv[1] ).read() )

reCommaEnd = re.compile(r',$')

for server in serverList:
	info = serverList[server]

	outDir = "data/%s/samples" % ( server )
	if not os.path.exists( outDir ):
		os.makedirs( outDir )

	try:
		db=MySQLdb.connect(host=info['host'],db=info['db'], passwd=info['passwd'], user=info['user'])
		cur = db.cursor()	
		cur.execute("select patDb, patField, sampleField, profile from raDb")	
		for row in cur.fetchall():
			name = row[0]
			patField = row[1]
			sampleField = row[2]
			cData = {
				'type' : 'sampleMap',
				'name' : name,
			}
			#print cData
			oHandle = open( "%s/%s.json" % (outDir, name), "w" )
			oHandle.write( json.dumps( cData ) )
			oHandle.close()				
			if name is not None:		
				try:
					cHost = serverList[ server ]
					db2=MySQLdb.connect(host=cHost['host'],db=name, passwd=cHost['passwd'], user=cHost['user'])		
					cur2 = db2.cursor()
					
					trackMap = {}
					cur2.execute( "select %s, %s from labTrack" % ( patField, sampleField ) )					
					for row2 in cur2.fetchall():
						if not trackMap.has_key( row2[0] ):
							trackMap[ row2[0] ] = []
						trackMap[ row2[0] ].append( row2[1] )
					
					oHandle = open( "%s/%s" % (outDir, name), "w" )
					for pat in trackMap:
						for sam in trackMap[ pat ]:							
							oHandle.write( "%s\t%s\n" % (pat, sam) )
					oHandle.close()					
					cur2.close()
				except _mysql_exceptions.ProgrammingError:
					pass
				
	except _mysql_exceptions.ProgrammingError, e:
		pass
