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
	outDir = "data/%s/genomic" % (server)
	if not os.path.exists( outDir ):
		os.makedirs(outDir)

	info = serverList[server]
	try:
		db=MySQLdb.connect(host=info['host'],db=info['db'], passwd=info['passwd'], user=info['user'])
		cur = db.cursor()	
		cur.execute("select name, wrangler, patDb, platform, aliasTable, profile, wrangler, wrangling_procedure from raDb")	
		for row in cur.fetchall():
			name = row[0]
			print name
			if name.endswith( '201103' ):
				continue
			gData = {
				'type': 'genomicMatrix',
				'name' : row[0],
				'author' : row[1],
				':sampleMap' : row[2],
				':dataSubType': row[3],
				':probeMap' : row[4],
				'author' : row[6],
				'notes' : row[7]
			}
			oHandle = open( "%s/%s.json" % (outDir, name), "w" )
			oHandle.write( json.dumps( gData ) )
			oHandle.close()
			
		
			#profile = row[5]
			#pHost = serverList[ profile ]
			pHost = info
			#if serverList.has_key( profile ):
				
			cur2 = db.cursor()
			cur2.execute( "select expIds, names from maDb where name='%s'" % ( name ) )
			row2 = cur2.fetchone()
			ids   = reCommaEnd.sub("", row2[0]).split(',')
			names = reCommaEnd.sub("", row2[1]).split(',')

			oHandle = open( "%s/%s" % (outDir, name), "w" )
			writer = csv.writer( oHandle, delimiter="\t" )

			row = ["NA"] * len(ids)
			for i in range( len(ids) ):
				row[ int(ids[i]) ] = names[i]
			cur2.close()
			row.insert(0, "probe")
			writer.writerow( row )
		
			try:
				db2 = MySQLdb.connect(host=pHost['host'],db=pHost['db'], passwd=pHost['passwd'], user=pHost['user'])
				cur2 = db2.cursor()
				cur2.execute( "select name, expIds, expScores from %s" % ( name ) )
				reading = True
				while reading:
					row2 = cur2.fetchone()
					if row2 is None:
						reading = False
					else:
						ids = reCommaEnd.sub("",row2[1]).split(',')
						scores = row2[2].split(',')
						row = ["NA"] * len(ids)
						#print len(ids)
						#print len(scores)
						for i in range(len(ids)):
							row[ int(ids[i]) ] = scores[i]
						row.insert(0, row2[0])
						writer.writerow( row )
				cur2.close()
				db2.close()
			except _mysql_exceptions.ProgrammingError, e:
				print "ERROR:", e
		
			oHandle.close()
			
	except _mysql_exceptions.ProgrammingError:
		pass
