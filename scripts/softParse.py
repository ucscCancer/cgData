#!/usr/bin/env python

import sys
import os
import json
import CGData.Soft
from optparse import OptionParser


if __name__ == "__main__":
    
    parser = OptionParser()
    
    
    parser.add_option("-l", "--list", dest="list", action="store_true", default=None)
    parser.add_option("-m", "--matrix", dest="matrix", default=None)
    parser.add_option("-c", "--clinical", action="store_true", dest="clinical", default=None)
    parser.add_option("-i", "--iddag", action="store_true", dest="iddag", default=None)
    parser.add_option("-a", "--aliasmap", dest="aliasmap", default=None)
    parser.add_option("--head", dest="head", default=None)
    
    (options, args) = parser.parse_args()
    
    soft_file = args[0]
    soft = CGData.Soft.Soft(soft_file + ".sqlite")
    if not os.path.exists(soft_file + ".sqlite" ):
        handle = open(soft_file)
        soft.read(handle)
        handle.close()
    
    if options.list is not None:
        for s in soft.get_section_list():
            print s
    
    if options.head is not None:
        for row in soft.get_col_list(options.head):
            print row
            
    if options.matrix is not None:
        out = soft.build_matrix(options.matrix, 'ID_REF')
        out.store(soft_file + ".matrix")

    if options.clinical is not None:
        out = soft.build_clinical()
        out.store(soft_file + ".clinical_matrix")

    if options.iddag is not None:
        out = soft.build_iddag()
        out.store(soft_file + ".iddag")

    if options.aliasmap is not None:
        out = soft.build_aliasmap(options.aliasmap, "Gene Symbol")
        out.store(soft_file + ".aliasmap")

    
