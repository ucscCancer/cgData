#!/usr/bin/env python

import sys
import os
import json
import shutil
from glob import glob




class CG1to2:
	
	types = {
		'sampleMap' : 'sampleMap',
		'clinicalFeature' : 'copy',
		'clinicalMatrix' : 'copy',
		'genomicMatrix' : 'copy'
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
					getattr(self, self.types[meta['type']])(path)

	def getmeta(self, path):
		handle = open(path)
		meta = json.loads(handle.read())
		handle.close()
		return meta

	def getdst(self,path):
		return os.path.abspath(path).replace(os.path.abspath(self.src), os.path.abspath(self.dst))

	def probeMap(self, path):
		print "probeMap", path, self.getdst(path)
	
	def sampleMap(self,path):
		meta = self.getmeta(path)
		meta['type'] = "idMap"
		handle = open( self.getdst(path), "w")
		handle.write( json.dumps(meta) )
		handle.close()
		dpath = path.replace(".json", "")
		shutil.copy( dpath, self.getdst(dpath) )		

	
	def copy(self,path):
		meta = self.getmeta(path)
		if ":sampleMap" in meta:
			meta[":idMap"] = meta[":sampleMap"]
			del meta[":sampleMap"]
		handle = open( self.getdst(path), "w")
		handle.write( json.dumps(meta) )
		handle.close()
		dpath = path.replace(".json", "")
		shutil.copy( dpath, self.getdst(dpath) )		


if __name__ == "__main__":
	endDir = sys.argv[-1]	
	for startDir in sys.argv[1:-1]:
		cg = CG1to2(startDir, endDir)
		cg.scan_path()
