#!/usr/bin/env python

import sys
import CGData.ClinicalMatrix

if __name__ == "__main__" : 
	
	matrix = None
	for p in sys.argv[1:]:
		nmatrix = CGData.ClinicalMatrix.ClinicalMatrix()
		nmatrix.load(p)
		matrix = nmatrix.merge(matrix)
	
	matrix.write(sys.stdout)
	
