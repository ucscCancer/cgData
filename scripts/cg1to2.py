#!/usr/bin/env python

import sys
import os
import json
import datetime
import shutil
from glob import glob
import csv

class CG1to2:
	
	types = {
		'sampleMap' : 'sampleMap',
		'clinicalFeature' : 'clinicalFeature',
		'clinicalMatrix' : 'clinicalMatrix',
		'genomicMatrix' : 'genomicMatrix',
		#'dataSubType' : 'copy',
		#'assembly' : 'copy',
		'probeMap' : 'probeMap',
		'genomicSegment' : 'genomicSegment'
	}
	
	def __init__(self, src, dst):
		self.src = src
		self.dst = dst

	def scan_path(self,path=None):
		if path is None:
			if self.src is not None:
				self.scan_path(self.src)
			return
		if os.path.isdir(path):
			if not os.path.exists( self.getdst(path) ):
				os.makedirs( self.getdst(path) )
			for cpath in glob( os.path.join( path, "*" ) ):
				self.scan_path(cpath)
		else:
			if path.endswith(".json"):
				meta = self.getmeta(path)
				if 'type' in meta and meta['type'] in self.types:
					print "processing:", path
					getattr(self, self.types[meta['type']])(path)

	def getmeta(self, path):
		handle = open(path)
		meta = json.loads(handle.read())
		handle.close()
		return meta

	def getdst(self,path):
		return os.path.abspath(path).replace(os.path.abspath(self.src), os.path.abspath(self.dst))

	def probeMap(self, path):		
		meta = self.getmeta(path)
		if 'group' in meta and meta['group'] is not None:
			meta['cgdata'] = { 'columnKeyMap' : { 'type' :'probe', 'name' : meta['group'] } }
			del meta['group']
		else:
			meta['cgdata'] = { 'columnKeyMap' : { 'type' :'probe', 'name' :meta['name'] } }
			
		meta = self.meta_adjust(meta) 
		handle = open( self.getdst(path), "w" )
		handle.write( json.dumps(meta))
		handle.close()
		
		apath = path.replace(".json", ".aliasmap.json")
		meta['cgdata']['type'] = 'aliasMap'
		handle = open( self.getdst(apath), "w" )
		handle.write( json.dumps(meta))
		handle.close()
		
		dpath = path.replace(".json", "")
		adpath = apath.replace(".json", "")
		ohandle = open( self.getdst(dpath), "w" )
		ahandle = open( self.getdst(adpath), "w" )
		owriter = csv.writer( ohandle, delimiter="\t", lineterminator="\n" )
		awriter = csv.writer( ahandle, delimiter="\t", lineterminator="\n" )
		handle = open(dpath)
		reader = csv.reader( handle, delimiter="\t")
		for row in reader:
			owriter.writerow( [row[0]] + row[2:] )
			if len(row[1]):
				awriter.writerow( row[0:2] )

		handle.close()
		ohandle.close()
		ahandle.close()
		
	def sampleMap(self,path):
		meta = self.getmeta(path)
		meta['type'] = "idMap"
		meta['cgdata'] = { 'columnKeyMap' : { 'type' : 'id', 'name' : meta['name'] } }
		self.copy(path,self.meta_adjust(meta))
		
	def clinicalFeature(self,path):
		meta = self.getmeta(path)
		meta['type'] = 'featureDescription'
		meta['cgdata'] = { 'columnKeyMap' : { 'type' : 'clinicalFeature', 'name' : meta['name'] } }
		self.copy(path,self.meta_adjust(meta))
	
	
	def genomicMatrix(self,path):
		meta = self.getmeta(path)
		meta['cgdata'] = { 
			'columnKeyMap' : { 'type' : 'probe', 'name' : meta[":probeMap"] },
			'rowKeyMap' : { 'type' : 'id', 'name' : meta[":sampleMap"] }		
		}
		del meta[':sampleMap']
		del meta[':probeMap']
		self.copy( path, self.meta_adjust(meta) )
	
	def genomicSegment(self,path):
		meta = self.getmeta(path)
		meta['cgdata'] = { 
			'rowKeyMap' : { 'type' : 'id', 'name' : meta[":sampleMap"] }		
		}
		del meta[':sampleMap']
		self.copy( path, self.meta_adjust(meta) )
	
	def clinicalMatrix(self,path):
		meta = self.getmeta(path)
		if ":clinicalFeature" in meta:
			meta['cgdata'] = { 
				'columnKeyMap' : { 'type' : 'clinicalFeature', 'name' : meta[":clinicalFeature"] },
				'rowKeyMap' : { 'type' : 'id', 'name' : meta[":sampleMap"] }		
			}
			del meta[':clinicalFeature']
		else:
			meta['cgdata'] = { 
				'rowKeyMap' : { 'type' : 'id', 'name' : meta[":sampleMap"] }		
			}
		del meta[':sampleMap']
		self.copy( path, self.meta_adjust(meta) )
	
	def meta_adjust(self, meta):
		if 'cgdata' not in meta:
			meta['cgdata'] = {}
		if 'name' in meta:
			meta['cgdata']['name'] = meta['name']
			del meta['name']
		if 'type' in meta:
			meta['cgdata']['type'] = meta['type']
			del meta['type']
		
		if 'date' in meta and meta['date'] is not None:
			meta['cgdata']['version'] = meta['date']
		else:
			meta['cgdata']['version'] = datetime.date.today().isoformat()
	
		if ":sampleMap" in meta:
			meta[":idMap"] = meta[":sampleMap"]
			del meta[":sampleMap"]
		
		rmlist = []
		meta['cgdata']['links'] = []
		for key in meta:
			if key.startswith( ":" ) :
				meta['cgdata']['links'].append( { 'type' : key[1:], 'name' : meta[key] } )
				rmlist.append(key)
		for key in rmlist:
			del meta[key]
		return meta
	
	def copy(self,path, meta=None):
		if meta is None:
			meta = self.getmeta(path)
			meta = self.meta_adjust(meta)

		handle = open( self.getdst(path), "w")
		handle.write( json.dumps(meta) )
		handle.close()
		dpath = path.replace(".json", "")
		if os.path.exists(dpath):
			shutil.copy( dpath, self.getdst(dpath) )		


if __name__ == "__main__":
	endDir = sys.argv[-1]	
	for startDir in sys.argv[1:-1]:
		cg = CG1to2(startDir, endDir)
		cg.scan_path()
