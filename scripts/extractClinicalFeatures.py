#!/usr/bin/env python

import MySQLdb
import _mysql_exceptions
import sys
import json
import csv
import re
import os
import traceback

serverList = json.loads( open( sys.argv[1] ).read() )

reCommaEnd = re.compile(r',$')

for server in serverList:
    info = serverList[server]

    outDir = "data/%s/clinicalFeature" % ( server )
    if not os.path.exists( outDir ):
        os.makedirs( outDir )

    try:
        db=MySQLdb.connect(host=info['host'],db=info['db'], passwd=info['passwd'], user=info['user'])
        cur = db.cursor()   
        cur.execute("select name, wrangler, patDb, platform, aliasTable, profile from raDb")    
        for row in cur.fetchall():
            name = row[0]
            print "patDB", name
            sampleMap = row[2]
            cData = {
                'type' : 'clinicalFeature',
                'name' : row[0],
                'author' : row[1]
            }
            #print cData
            oHandle = open( "%s/%s.json" % (outDir, name), "w" )
            oHandle.write( json.dumps( cData ) )
            oHandle.close()
                    
            profile = row[5]

            cur2 = db.cursor()
            cur2.execute( "select name, shortLabel, longLabel, sampleField, valField, tableName, filterType from colDb where dataset='%s'" % (name) ) # where dataset='%s' " % (name) )
            fMap = {}           
            for row2 in cur2.fetchall():
                fData = {
                    'name' : row2[0],
                    'shortLabel' : row2[1],
                    'longLabel' : row2[2],
                    'sampleField' : row2[3],
                    'valField' : row2[4],
                    'tableName' : row2[5],
                    'filterType' : row2[6]
                }
                fMap[ row2[0] ] = fData
            cur2.close()
            
            if len(fMap) == 0:
                print name, " has no clinical features"
            
            if sampleMap is not None:     
                try:
                    cHost = serverList[ server ]
                    print "sampleMap", sampleMap
                    db2=MySQLdb.connect(host=cHost['host'],db=sampleMap, passwd=cHost['passwd'], user=cHost['user'])      
                    cur2 = db2.cursor()
                    
                    fEnum = {}
                    cur2.execute( "select tableName, colName, code, val from codes" )       
                    for row2 in cur2.fetchall():
                        if not fEnum.has_key( row2[0] ):
                            fEnum[ row2[0] ] = {}
                        if not fEnum[ row2[0] ].has_key( row2[1] ):
                            fEnum[ row2[0] ][ row2[1] ] = {}
                        fEnum[ row2[0] ][ row2[1] ][ row2[2] ] = row2[3]
                    
                    
                    fCols = {}    
                    fVals = {}
                    for fName in fMap:
                        try:
                            sampleField = fMap[fName]['sampleField']
                            colName = fMap[fName]['name']
                            tableName = fMap[fName]['tableName']
                            query = "select %s, %s from %s" % ( sampleField, colName, tableName )
                            #print query
                            cur2.execute( query )                   
                            for row2 in cur2.fetchall():
                                if not fVals.has_key( row2[0] ):
                                    fVals[ row2[0] ] = {}
                                if not fVals[ row2[0] ].has_key( fName ):
                                    fVals[ row2[0] ][ fName ] = {}
                                
                                try:
                                    fVals[ row2[0] ][ fName ] = fEnum[ tableName ][ colName ][ row2[1] ]
                                except KeyError:
                                    fCols[ fName ] = True
                                    fVals[ row2[0] ][ fName ] = str( row2[1] )
                            
                        except _mysql_exceptions.OperationalError, e:
                            pass
                    
                    
                    
                    oHandle = open( "%s/%s" % (outDir, name), "w" )

                    for n in fCols:
                        oHandle.write("%s\tshortTitle\t%s\n" % (n, fMap[n]['shortLabel']))
                        if fMap[n]['shortLabel'] != fMap[n]['longLabel']:
                            oHandle.write("%s\tlongTitle\t%s\n" % (n, fMap[n]['longLabel']))
                        oHandle.write("%s\tvalueType\tfloat\n\n" % (n))
                    
                    for n in fEnum:
                        for f in fEnum[n]:
                            if f in fMap:
                                oHandle.write("%s\tshortTitle\t%s\n" % (n, fMap[f]['shortLabel']))
                                if fMap[f]['longLabel'] != fMap[f]['shortLabel']:
                                    oHandle.write("%s\tlongTitle\t%s\n" % (n, fMap[f]['longLabel']))
                            oHandle.write("%s\tvalueType\tcategory\n" % (f))
                            
                            l = [None] * (max(fEnum[n][f].keys())+1)
                            for t in fEnum[n][f]:
                                oHandle.write("%s\tstate\t%s\n" % (f,fEnum[n][f][t]))
                                l[t] = fEnum[n][f][t].replace(",", "\,")
                            
                            while l.count(None):
                                l.remove(None)
                            
                            oHandle.write("%s\tstateOrder\t%s\n" % (f,",".join(l)))
                            
                            
                            oHandle.write("\n")
                    
                    
                    
                    
                    oHandle.close()
                    
                    """
                    cur3 = db2.cursor(MySQLdb.cursors.DictCursor)
                    cur3.execute( "select * from %s" % (cData['sampleMap']) )
                    for row3 in cur3.fetchall():
                        print row3
                    
                    cur3.close()

                    
                            
                    for fName in fMap:
                        try:
                            sampleField = fMap[fName]['sampleField']
                            colName = fMap[fName]['name']
                            tableName = fMap[fName]['tableName']
                            query = "select %s, %s from %s" % ( sampleField, colName, tableName )
                            #print query
                            cur2.execute( query )                   
                            for row2 in cur2.fetchall():
                                if not fVals.has_key( row2[0] ):
                                    fVals[ row2[0] ] = {}
                                if not fVals[ row2[0] ].has_key( fName ):
                                    fVals[ row2[0] ][ fName ] = {}
                                
                                try:
                                    fVals[ row2[0] ][ fName ] = fEnum[ tableName ][ colName ][ row2[1] ]
                                except KeyError:
                                    fVals[ row2[0] ][ fName ] = str( row2[1] )
                            
                        except _mysql_exceptions.OperationalError, e:
                            pass
                    
                    oHandle = open( "%s/%s" % (outDir, name), "w" )
            
                    head = sorted( fMap.keys() )
                    oHandle.write( "Sample\t%s\n" % ( "\t".join(head) ) )
                    for sample in fVals:
                        out = []
                        for col in head:
                            if ( fVals[ sample ].has_key( col ) ):
                                out.append( fVals[ sample ][ col ] )
                            else:
                                out.append( "NA" )
                        oHandle.write( "%s\t%s\n" % (sample, "\t".join(out) ) )

                    oHandle.close()
                    """
                    
                    
                    
                    cur2.close()
                except _mysql_exceptions.ProgrammingError, e:
                    traceback.print_exc()
                    
    except _mysql_exceptions.ProgrammingError, e:
        pass

