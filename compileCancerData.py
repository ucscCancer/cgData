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

SAMPLE_FIELD = "sampleSpace"
PROBE_FIELD = "probeSpace"


includeList = None


CREATE_raDb = """
CREATE TABLE raDb (
    id int unsigned,	# Unique id
    name varchar(255),	# Table name for genomic data
    accessTable varchar(255),	# Down-sampled table
    shortLabel varchar(255),	# Short label
    longLabel varchar(255),	# Long label
    expCount int unsigned,	# Number of samples
    height int unsigned,	# Image Height (only for bed 4)
    groupName varchar(255),	# Group name
    raFile varchar(255),	# RA file containing clinical info
    patDb varchar(255),	# Clinical info db
    microscope varchar(255),	# hgMicroscope on/off flag
    sampleField varchar(255),	# Sample field
    patTable varchar(255),	# Patient to sample mapping
    patField varchar(255),	# Patient field
    aliasTable varchar(255),	# Probe to gene mapping
    displayNameTable varchar(255),	# Display names for aliases
    dataType varchar(255),	# data type (bed 15)
    platform varchar(255),	# Expression, SNP, etc.
    gain float,	# Gain
    type varchar(255),	# Unknown
    visibility varchar(255),	# Default visibility
    priority float,	# Priority for sorting
    url varchar(255),	# Pubmed URL
    security varchar(255),	# Security setting (public, private)
    profile varchar(255),	# Database profile
    wrangler varchar(255),	# Wrangler
    citation varchar(255),	# Citation
    article_title longblob,	# Title of publication
    author_list longblob,	# Author list
    wrangling_procedure longblob,	# Wrangling
              #Indices
    PRIMARY KEY(id)
);
"""

CREATE_colDb = """
#columnDb info
CREATE TABLE colDb (
    id int unsigned,	# Unique id
    dataset varchar(255),	# Dataset table name - matching 'name' in raDb
    name varchar(255),	# Column name
    shortLabel varchar(255),	# Short label
    longLabel varchar(255),	# Long label
    sampleField varchar(255),	# Sample field name
    valField varchar(255),	# Val field name
    colTable varchar(255),	# Table of clinical data
    priority float,	# Priority
    filterType varchar(255),	# Filter Type - minMax or coded
    visibility varchar(255),	# Visibility
    groupName varchar(255),	# Group Name
              #Indices
    PRIMARY KEY(id)
);
"""

CREATE_maDb = """
#maDb info
CREATE TABLE maDb (
    id int unsigned,	# Unique id
    name varchar(255),	# Microarray group name
    size int unsigned,	# Number of samples
    expIds longblob,	# Sample indices into bed15 table
    names longblob,	# Sample names
              #Indices
    PRIMARY KEY(id)
);
"""

def genomicMatrix( path, info ):
	#create bed15 files to be loaded 
	print "Create Genomic Matrix", path

def featureMatrix(path, info):
	print "Create Feature Matrix", path
	
	if info[ SAMPLE_FIELD ] is None:
		return
		
	basename = os.path.join( OUT_DIR, info[ SAMPLE_FIELD ] )
	print basename
	inPath = reJson.sub( "", path )
	if not os.path.exists( inPath ):
		return
	handle = open( inPath )
	
	oHandle = open( "%s.columnDb_clinical.ra" % (basename), "w" )
	sHandle = open( "%s.codes.sql" % (basename), "w")
	sHandle.write("""
drop table if exists codes ;
CREATE TABLE codes	(
	tableName varchar(255) default NULL,
	colName varchar(255) default NULL,
	code int(11) default NULL,
	val varchar(255) default NULL
) ;
""")
	
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
				colHash[ colName[i] ][ row[0] ] = row[i]
			targetSet.append( row[0].rstrip() )
	handle.close()
	
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
	
	showList = None	
	if os.path.exists( "important.list" ):
		handle = open( "important.list" )
		showList = {}
		for line in handle:
			tmp = line.rstrip().split(' ')
			showList[ tmp[0] ] = tmp[1]
	
	def colFix( name ):
		out = name.replace( '-', '_' )
		while (len(out) > 64):
			out = re.sub( r'[aeiou]([^aioeu]*)$', r'\1', out)
		return out
		
	for name in floatMap:
		idMap[ name ] = idNum
		idNum += 1	
		#colName = "clinicalData_%d" % ( int(idNum) )
		colName = colFix( name )
		colOrder.append( colName )
		origOrder.append( name )
		oHandle.write("name %s\n" % (colName) )
		oHandle.write("shortLabel %s\n" % (name) )
		oHandle.write("longLabel %s\n" % (name) )
		if showList is None or not showList.has_key( name ):
			oHandle.write("priority %d\n" % (prior) )
			prior += 1
		else:
			oHandle.write("priority %s\n" % ( showList[name] ) )
	
		if ( showList is None or showList.has_key( name ) ):
			oHandle.write("visibility on\n")
		else:
			oHandle.write("visibility off\n")
	
		
		oHandle.write("type lookup clinicalFeatures patientId %s\n" % (colName) )
		oHandle.write("filterType minMax\n\n")
	
	for name in enumMap:
		idMap[ name ] = idNum
		idNum += 1	
		#colName = "clinicalData_%d" % ( int(idNum) )
		colName = colFix( name )
		colOrder.append( colName )
		origOrder.append( name )
		oHandle.write("name %s\n" % (colName) )
		oHandle.write("shortLabel %s\n" % (name) )
		oHandle.write("longLabel %s\n" % (name) )
		if showList is None or not showList.has_key( name ):
			oHandle.write("priority %d\n" % (prior) )
			prior += 1
		else:
			oHandle.write("priority %s\n" % ( showList[name] ) )
	
		if ( showList is None or showList.has_key( name ) ):
			oHandle.write("visibility on\n")
		else:
			oHandle.write("visibility off\n")
		
		oHandle.write("type lookup clinicalFeatures patientId %s\n" % (colName) )
	
		oHandle.write("filterType coded\n\n")
		for enum in enumMap[ name ]:
			sHandle.write( "INSERT INTO codes VALUES( '%s','%s',%d,'%s' );\n" % 
				( "clinicalFeatures", colName,  enumMap[name][enum], enum.replace("'", "\\'")  ) )
	
	sHandle.close()
	oHandle.close()	
	
	dHandle = open( "%s.data.sql" % (basename), "w")
	dHandle.write("""
drop table if exists clinicalFeatures ;
CREATE TABLE clinicalFeatures (
patientID varchar(255) default NULL""")
	for col in colOrder:
		if ( colHash.has_key( col ) ):
			dHandle.write(",\n\t%s INTEGER default NULL" % (col) )
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
				if enumMap.has_key( col ):
					val = enumMap[col][ val ]
				a.append( "'" + str(val) + "'" )
		dHandle.write(" INSERT INTO clinicalFeatures VALUES ( '%s', %s );\n" % ( target, ",".join(a) ) )
	dHandle.close()
		
	lHandle = open( "%s.labTrack.sql" % (basename), "w")
	lHandle.write("""
drop table if exists labTrack ;
CREATE TABLE labTrack (
	patientId varchar(255),
	trackId   varchar(255)
);
""")
	
	for target in targetSet:
		lHandle.write( "INSERT INTO labTrack VALUES( '%s', '%s' );\n" % (target, target) )
	lHandle.close()



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

def genomicFeatureMapping( leftPath, leftInfo, rightPath, rightInfo ):
	#create raDB entries 
	if leftInfo[ SAMPLE_FIELD ] == rightInfo[ SAMPLE_FIELD ]:
		print "feature mapping", leftInfo, "  ", rightInfo

def genomicProbeMapping( leftPath, leftInfo, rightPath, rightInfo ):
	if leftInfo[ PROBE_FIELD ] == rightInfo[ PROBE_FIELD ]:
		if includeList is not None and not includeList.has_key( leftInfo[ 'name' ] ):
			return 
		print "probe mapping", leftPath, "  ", rightPath
		basename = os.path.join( OUT_DIR, leftInfo[ 'name' ] )
		print basename
		print leftPath, rightPath
		rPath = reJson.sub( "", rightPath )
		lPath = reJson.sub( "", leftPath )
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
		oHandle = open( "%s.bed15.sql" % (basename), "w" )
		oHandle.write( CREATE_BED % ( leftInfo[ 'name' ]  ) )
		
		head = None
		for line in read:
			if head is None:
				head = line
			else:
				probe = line[0]
				expIDs = ','.join( str(a) for a in range(1,len(line)))
				exps = ','.join( str(a) for a in line[1:])

				iStr = "insert into %s(chrom, chromStart, chromEnd, strand,  name, expCount, expIds, expScores) values ( '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s' );\n" % \
					( leftInfo[ 'name' ], probeHash[probe]['chrom'], probeHash[probe]['start'], probeHash[probe]['end'], probeHash[probe]['strand'], probe, len(line), expIDs, exps )
				
				oHandle.write( iStr )
		oHandle.close()
		
		#run matrix2bed code

def probeMatrix(path, info):	
	if info[ PROBE_FIELD ] is not None:
		basename = os.path.join( OUT_DIR, info[ PROBE_FIELD ] )
		print basename
		if os.path.exists( basename ):
			handle = open( reJson.sub( "", path ) )
			read = csv.reader( handle, delimiter="\t" )
			
			oHandle = open( "%s.alias.sql" % (basename), "w" )
			
			for row in read:
				oHandle.write("INSERT into test values( '%s', %s, %s, '%s' );\n" % (row[0], row[1], row[2], row[3] ) )
			handle.close()
			oHandle.close()
	
setMap = { 
	"type" : { 
		"genomic" : genomicMatrix, 
		"feature" : featureMatrix, 
		"probeMap" : probeMatrix 
	} 
}

setHash = {}

setCombine = {
	"type" : { 
		"genomic" : { "feature" : genomicFeatureMapping, "probeMap" : genomicProbeMapping }
	}
}


if __name__ == "__main__":

	opts, args = getopt( sys.argv[1:], "l:" )
		
	for a,o in opts:
		if a == "-l":
			handle = open( o )
			includeList = {}
			for line in handle:
				includeList[ line.rstrip() ] = True
			handle.close()
		

	for field in setMap:
		setHash[field] = {}
		for type in setMap[ field ]:
			setHash[ field ][ type ] = {}

	for dir in args:
		sys.stderr.write("DIR: %s\n" % (dir) )
		for path in glob( os.path.join( dir, "*.json" ) ):
			handle = open( path )
			data = json.loads( handle.read() )
			for field in setMap:
				if data.has_key( field ) and setMap[ field ].has_key( data[field] ):
					setHash[field][data[field]][ path ] = data
			handle.close()

	print setHash

	for field in setHash:
		for type in setHash[ field ]:
			for path in setHash[ field ][ type ]:
				try:
					setMap[ field ][type]( path, setHash[ field ][type][path] )
				except KeyError:
					pass

					
	for field in setCombine:
		for lType in setHash[ field ]:
			for lPath in setHash[ field ][ lType ]:
				for rType in setHash[ field ]:
					for rPath in setHash[ field ][ rType ]:
						try:
							setCombine[ field ][ lType ][ rType ]( lPath, setHash[ field ][ lType ][ lPath ], rPath, setHash[ field ][ rType ][ rPath ] )
						except KeyError:
							pass

