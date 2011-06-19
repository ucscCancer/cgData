#!/usr/bin/env python

import os
import sys
from glob import glob
import json
import re
import csv
from getopt import getopt
reJson = re.compile( r'.json$' )

OUT_DIR = "genRA"

TYPE_FIELD = "type"
TYPE_GENOMIC = "genomic"
TYPE_FEATURE = "feature"

SAMPLE_FIELD = "sampleMap"
PROBE_FIELD = "probeMap"

DATABASE_NAME = "hg18"

errorLogHandle = None
def error(eStr):
	sys.stderr.write("ERROR: %s\n" % (eStr) )
	errorLogHandle.write( "ERROR: %s\n" % (eStr) )

def warn(eStr):
	sys.stderr.write("WARNING: %s\n" % (eStr) )
	errorLogHandle.write( "WARNING: %s\n" % (eStr) )

def log(eStr):
	sys.stderr.write("LOG: %s\n" % (eStr) )
	errorLogHandle.write( "LOG: %s\n" % (eStr) )


includeList = None

raDbHandle = None

CREATE_colDb = """
CREATE TABLE `%s` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) default NULL,
  `shortLabel` varchar(255) default NULL,
  `longLabel` varchar(255) default NULL,
  `valField` varchar(255) default NULL,
  `tableName` varchar(255) default NULL,
  `priority` float default NULL,
  `filterType` varchar(255) default NULL,
  `visibility` varchar(255) default NULL,
  `groupName` varchar(255) default NULL,
  PRIMARY KEY  (`id`),
  KEY `name` (`name`)
);
"""


CREATE_BED = """
CREATE TABLE %s (
    bin smallint unsigned not null,
    chrom varchar(255) not null,
    chromStart int unsigned not null,
    chromEnd int unsigned not null,
    name varchar(255) not null,
    score int not null,
    strand char(1) not null,
    thickStart int unsigned not null,
    thickEnd int unsigned not null,
    reserved int unsigned  not null,
    blockCount int unsigned not null,
    blockSizes longblob not null,
    chromStarts longblob not null,
    expCount int unsigned not null,
    expIds longblob not null,
    expScores longblob not null,
    INDEX(name(16)),
    INDEX(chrom(4),chromStart),
    INDEX(chrom(4),bin)
);
"""


def colFix( name ):
	out = name.replace( '-', '_' )
	while (len(out) > 64):
		out = re.sub( r'[aeiou]([^aioeu]*)$', r'\1', out)
	return out

def sqlFix( name ):
	return name.replace("'", "\\'")

def genomicClinicalMapping( sampleMap, genomicPath, genomeInfo, featurePath, featureInfo ):
	#create raDB entries 
	if genomeInfo[ SAMPLE_FIELD ] != featureInfo[ SAMPLE_FIELD ]:
		return
	
	if featureInfo[ SAMPLE_FIELD ] is None:
		return

	print "feature mapping", genomicPath, "  ", featurePath
		
	basename = os.path.join( OUT_DIR, "%s_clinical_%s" % ( DATABASE_NAME, featureInfo[ SAMPLE_FIELD ] ) )
	print basename
	inPath = reJson.sub( "", featurePath )
	if not os.path.exists( inPath ):
		return
	handle = open( inPath )		
	read = csv.reader( handle, delimiter="\t" )
	
	colName = None
	colHash = {}
	targetSet = []
	for row in read:
		if colName is None:
			colName = row
			for name in colName[1:]:
				colHash[ name ] = {}
		else:
			for i in range( 1, len(row) ):
				colHash[ colName[i] ][ row[0].rstrip() ] = row[i]
			targetSet.append( row[0].rstrip() )
	handle.close()
	
	#print colHash
	
	floatMap = {}
	enumMap = {}
	for key in colHash:
		isFloat = True
		hasVal = False
		enumSet = {}
		for sample in colHash[ key ]:
			try:
				#print colHash[ key ][ sample ]
				value = colHash[ key ][ sample ]
				if value != "null" and len(value):
					hasVal = True
					if not enumSet.has_key( value ):
						enumSet[ value ] = len( enumSet )
					a = float(value)
			except ValueError:
				isFloat = False
		if hasVal:
			if isFloat:
				floatMap[ key ] = True
			else:
				enumMap[ key ] = enumSet
		
	#print floatMap
	#print enumMap
	
	idMap = {}
	idNum = 0
	prior = 1
	colOrder = []
	origOrder = []	

	for name in floatMap:
		idMap[ name ] = idNum
		idNum += 1	
		colName = colFix( name )
		colOrder.append( colName )
		origOrder.append( name )
		
	for name in enumMap:		
		idMap[ name ] = idNum
		idNum += 1	
		colName = colFix( name )
		colOrder.append( colName )
		origOrder.append( name )		
	
	dHandle = open( "%s.sql" % (basename), "w")
	dHandle.write("drop table if exists clinical_%s;" % ( featureInfo[ 'name' ] ) )
	dHandle.write("""
CREATE TABLE clinical_%s (
\tsampleID int""" % ( featureInfo[ 'name' ] ))
	for col in colOrder:
		if ( enumMap.has_key( col ) ):
			dHandle.write(",\n\t%s ENUM( '%s' ) default NULL" % (col, "','".join(enumMap[ col ].keys() ) ) )
		else:
			dHandle.write(",\n\t%s FLOAT default NULL" % (col) )		
	dHandle.write("""
) ;	
""")
	
	for target in targetSet:
		a = []
		for col in origOrder:
			val = colHash[ col ].get( target, None )
			#print target, col, val
			if val is None or val == "null" or len(val) == 0 :
				a.append("\N")
			else:				
				a.append( "'" + str(val) + "'" )
		dHandle.write("INSERT INTO clinical_%s VALUES ( %d, %s );\n" % ( featureInfo[ 'name' ], sampleMap[ target ], ",".join(a) ) )
	dHandle.close()

	cHandle = open( "%s_colDb.sql" % (basename), "w" )
	cHandle.write("drop table if exists clinical_%s_colDb;" % ( featureInfo[ 'name' ] ) )
	cHandle.write( CREATE_colDb % ( "clinical_" + featureInfo[ 'name' ] + "_colDb" ) )
	"""
`id` int(10) unsigned NOT NULL default '0',
  `name` varchar(255) default NULL,
  `shortLabel` varchar(255) default NULL,
  `longLabel` varchar(255) default NULL,
  `valField` varchar(255) default NULL,
  `tableName` varchar(255) default NULL,
  `priority` float default NULL,
  `filterType` varchar(255) default NULL,
  `visibility` varchar(255) default NULL,
  `groupName` varchar(255) default NULL,
  PRIMARY KEY  (`id`),
  KEY `name` (`name`)
	"""
	for name in colOrder:
		cHandle.write("INSERT INTO clinical_%s_colDb(name, shortLabel,longLabel,valField,tableName) VALUES( '%s', '%s', '%s', '%s', '%s' );\n" % \
			( featureInfo[ 'name' ], name, name, name, name, "clinical_" + featureInfo[ 'name' ] ) )
	cHandle.close()
		
	
		

def genomicProbeMapping( sampleMap, genomicPath, genomeInfo, probePath, probeInfo ):
	if genomeInfo[ PROBE_FIELD ] == probeInfo[ 'name' ] and sampleMap is not None:
		if includeList is not None and not includeList.has_key( genomeInfo[ 'name' ] ):
			return 
		print "probe mapping", genomicPath, "  ", probePath
		basename = os.path.join( OUT_DIR, "%s_genomic_%s" % ( DATABASE_NAME, genomeInfo[ 'name' ] ) )
		print basename
		rPath = reJson.sub( "", probePath )
		lPath = reJson.sub( "", genomicPath )
		if not os.path.exists( rPath ) or not os.path.exists( lPath ):
			return
		rHandle = open( rPath )
		read = csv.reader( rHandle, delimiter="\t" )
		probeHash = {}
		for line in read:
			probeHash[ line[0] ] = { 'chrom' : line[1], 'start' : line[2], 'end' : line[3], 'strand' : line[4], 'alias' : line[5].split(',') }
		rHandle.close()
		
		lHandle = open( lPath )
		read = csv.reader( lHandle, delimiter="\t")
		oHandle = open( "%s.sql" % (basename), "w" )
		oHandle.write("drop table if exists genomic_%s;" % ( genomeInfo[ 'name' ] ) )
		oHandle.write( CREATE_BED % ( "genomic_" + genomeInfo[ 'name' ]  ) )
		
		head = None
		for line in read:
			if head is None:
				head = line
			else:
				probe = line[0]
				sampleIDs = []
				for a in head[1:]:
					try:
						sampleIDs.append( str(sampleMap[a]) )
					except KeyError:
						error( "UNKNOWN SAMPLE: %s" % (a) )
						sampleIDs = None
						break
					
				if sampleIDs is not None:
					expIDs = ','.join( sampleIDs )
					exps = ','.join( str(a) for a in line[1:])
					try:
						iStr = "insert into %s(chrom, chromStart, chromEnd, strand,  name, expCount, expIds, expScores) values ( '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s' );\n" % \
						( "genomic_%s" % (genomeInfo[ 'name' ]), probeHash[probe]['chrom'], probeHash[probe]['start'], probeHash[probe]['end'], probeHash[probe]['strand'], probe, len(line), expIDs, exps )
						oHandle.write( iStr )
					except KeyError:
						error( "MISSING PROBE: %s" % ( probe ) )
		oHandle.close()
	
		handle = open( rPath )
		read = csv.reader( handle, delimiter="\t" )
		
		oHandle = open( "%s_alias.sql" % (basename), "w" )
		oHandle.write("drop table if exists genomic_%s_alias;" % ( genomeInfo[ 'name' ] ) )
		oHandle.write("""
CREATE TABLE genomic_%s_alias (
\tname varchar(255) default NULL,
\talias varchar(255) default NULL
);
""" % ( genomeInfo[ 'name' ] ) )
		for row in read:
			for alias in row[5].rstrip().split(','):
				if len(alias):
					oHandle.write("INSERT into genomic_%s_alias values ( '%s', '%s' );\n" % (genomeInfo[ 'name' ], sqlFix(row[0]), sqlFix(alias) ) ) 
		handle.close()
		oHandle.close()




def genomicSampleMapping( genomicPath, genomeInfo, samplePath, sampleInfo ):	
	basename = os.path.join( OUT_DIR, "%s_sample_%s" % ( DATABASE_NAME, sampleInfo[ 'name' ] ) )

	lPath = reJson.sub( "", samplePath )
	if not os.path.exists( lPath ):
		return
	rHandle = open( lPath )
	read = csv.reader( rHandle, delimiter="\t" )
	targetHash = {}
	for target in read:
		targetHash[ target[0] ] = target[1]
		targetHash[ target[1] ] = None
	
	keySet = targetHash.keys()
	keySet.sort()
	
	lHandle = open( "%s.sql" % (basename), "w")
	lHandle.write("drop table if exists sample_%s;" % ( sampleInfo[ 'name' ] ) )

	lHandle.write("""
CREATE TABLE sample_%s (
	id           int,
	sampleName   varchar(255)
);
""" % ( sampleInfo[ 'name' ] ) )
	
	sampleHash = {}
	for i in range( len( keySet ) ):
		lHandle.write( "INSERT INTO sample_%s VALUES( %d, '%s' );\n" % ( sampleInfo[ 'name' ], i, keySet[i] ) )
		sampleHash[  keySet[i] ] = i
	lHandle.close()
	return sampleHash
	


if __name__ == "__main__":
	opts, args = getopt( sys.argv[1:], "d:l:" )
	for a,o in opts:
		if a == "-l":
			handle = open( o )
			includeList = {}
			for line in handle:
				includeList[ line.rstrip() ] = True
			handle.close()
		if a == "-d":
			DATABASE_NAME = o


	errorLogHandle = open( "error.log", "w" )

	raDbHandle = open( os.path.join( OUT_DIR, "%s_raDb.sql" % (DATABASE_NAME) ), "w" )
	#raDbHandle.write( CREATE_raDb  )

	setHash = {  'genomic' : {}, "clinical" : {}, "probeMap" : {}, "sampleMap" : {} }
	pathHash = {  'genomic' : {}, "clinical" : {}, "probeMap" : {}, "sampleMap" : {} }

	for dir in args:
		log("SCANNING DIR: %s" % (dir) )
		for path in glob( os.path.join( dir, "*.json" ) ):
			handle = open( path )
			data = json.loads( handle.read() )
			if data.has_key( 'name' ) and data.has_key( 'type' ) and setHash.has_key( data['type'] ) :
				if setHash[ data['type'] ].has_key( data['name'] ):
					error( "Duplicate %s file %s" % ( data['type'], data['name'] ) )
				setHash[data['type'] ][ data['name'] ] = data
				pathHash[data['type'] ][ data['name'] ] = path				
			else:
				warn( "Unknown file type: %s" % ( path ) )
			handle.close()
			
	#print setHash

	for genomicName in setHash[ 'genomic' ]:
		genomicData = setHash[ 'genomic' ][ genomicName ]
		if genomicData[ 'probeMap' ] is None:
			error("%s lacks probeMap" % ( genomicName ) )
			continue

		if genomicData[ 'sampleMap' ] is None:
			error("%s lacks sampleMap" % ( genomicName ) )
			continue

		if setHash[ 'probeMap' ].has_key( genomicData[ 'probeMap' ] ):
			probeData = setHash[ 'probeMap' ][ genomicData[ 'probeMap' ] ]
			probeName = genomicData[ 'probeMap' ]
		else:
			error( "%s Missing Probe Data: %s" % ( genomicName, genomicData[ 'probeMap' ] ) )
				
		if setHash[ 'sampleMap' ].has_key( genomicData[ 'sampleMap' ] ):
			sampleData = setHash[ 'sampleMap' ][ genomicData[ 'sampleMap' ] ]
			sampleName = genomicData[ 'sampleMap' ]
		else:
			error( "%s Missing Sample Data: %s" % ( genomicName, genomicData[ 'sampleMap' ] ) )	


		clinicalList = []
		clinicalNames = []
		for clinSet in setHash[ 'clinical' ]:
			if setHash[ 'clinical' ][ clinSet ][ 'name' ] == sampleData[ 'name' ]:
				clinicalList.append( setHash[ 'clinical' ][ clinSet ] )
				clinicalNames.append( clinSet )
		
		print genomicName, genomicData, probeData, sampleData
		print clinicalList		
		
		sampleMap = genomicSampleMapping( pathHash[ 'genomic' ][ genomicName ], genomicData, 
			pathHash[ 'sampleMap' ][ sampleName ], sampleData )
			
		print sampleMap
		genomicClinicalMapping( sampleMap, pathHash[ 'genomic' ][ genomicName ], genomicData, 
			pathHash[ 'clinical' ][ clinicalNames[0] ], clinicalList[0] )

		genomicProbeMapping( sampleMap, pathHash[ 'genomic' ][ genomicName ], genomicData, 
			pathHash[ 'probeMap' ][ probeName ], probeData )
		"""
		`name` varchar(255) default NULL,
		`downSampleTable` varchar(255) default NULL,
		`sampleTable` varchar(255) default NULL,
		`clinicalTable` varchar(255) default NULL,
		`columnTable` varchar(255) default NULL,
		`shortLabel` varchar(255) default NULL,
		`longLabel` varchar(255) default NULL,
		`expCount` int(10) unsigned default NULL,
		`groupName` varchar(255) default NULL,
		`microscope` varchar(255) default NULL,
		`aliasTable` varchar(255) default NULL,
		`dataType` varchar(255) default NULL,
		`platform` varchar(255) default NULL,
		`security` varchar(255) default NULL,
		`profile` varchar(255) default NULL,
		"""
		raDbHandle.write( "INSERT into raDb( name, sampleTable, clinicalTable, columnTable, aliasTable, shortLabel) VALUES ( '%s', '%s', '%s', '%s', '%s', '%s');\n" % \
			( "genomic_" + genomicName, "sample_" + sampleName, "clinical_" + clinicalNames[0], "clinical_" + clinicalNames[0] + "_colDb", "genomic_" + genomicName + "_alias", genomicName ))
		raDbHandle.flush()
		
	errorLogHandle.close()
	raDbHandle.close()
