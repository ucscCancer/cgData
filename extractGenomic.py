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

if not os.path.exists( "data/genomic" ):
	os.makedirs("data/genomic")

for server in serverList:
	info = serverList[server]
	try:
		db=MySQLdb.connect(host=info['host'],db=info['db'], passwd=info['passwd'], user=info['user'])
		cur = db.cursor()	
		cur.execute("select name, wrangler, patDb, platform, aliasTable, profile from raDb")	
		for row in cur.fetchall():
			name = row[0]
			print name
			gData = {
				'name' : row[0],
				'author' : row[1],
				'sampleSpace' : row[2],
				'platform': row[3],
				'probeSpace' : row[4]
			}
			oHandle = open( "data/genomic/%s.json" % (name), "w" )
			oHandle.write( json.dumps( gData ) )
			oHandle.close()
			
		
			profile = row[5]

			if serverList.has_key( profile ):
				
				cur2 = db.cursor()
				cur2.execute( "select expIds, names from maDb where name='%s'" % ( name ) )
				row2 = cur2.fetchone()
				ids   = reCommaEnd.sub("", row2[0]).split(',')
				names = reCommaEnd.sub("", row2[1]).split(',')

				oHandle = open( "data/genomic/%s" % (name), "w" )
				writer = csv.writer( oHandle, delimiter="\t" )

				row = ["NA"] * len(ids)
				for i in range( len(ids) ):
					row[ int(ids[i]) ] = names[i]
				cur2.close()
				row.insert(0, "probe")
				writer.writerow( row )
			
				pHost = serverList[ profile ]
				try:
					db2 = MySQLdb.connect(host=pHost['host'],db=pHost['db'], passwd=pHost['passwd'], user=pHost['user'])
					cur2 = db2.cursor()
					cur2.execute( "select name, expIds, expScores from %s" % ( name ) )
					for row2 in cur2.fetchall():
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
