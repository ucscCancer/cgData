#!/usr/bin/env python

import sys
import CGData.IDDag


if __name__ == "__main__":
	matrix = CGData.load(sys.argv[1])
	idDag = CGData.load(sys.argv[2])
	red = CGData.IDDag.IDReducer(idDag)
	omatrix = red.reduce_matrix(matrix, sys.argv[3])
	omatrix.write( sys.stdout )