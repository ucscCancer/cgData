#!/usr/bin/env python

import sys
import csv

import CGData.GenomicSegment
import CGData.GeneMap
import CGData.RefGene
import CGData.GenomicMatrix
import numpy

handle = open( sys.argv[1] )
sg = CGData.GenomicSegment.GenomicSegment()
sg.read( handle )
sg.loaded = True
handle.close()

handle = open( sys.argv[2] )
rg = CGData.RefGene.RefGene()
rg.read( handle )
handle.close()

pm = CGData.GeneMap.ProbeMapper('b')

out = CGData.GeneMap.genomicSegment2MatrixNorm(sg,rg,pm)
out.write(sys.stdout)

