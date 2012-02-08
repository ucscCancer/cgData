#!/usr/bin/env python

import sys
import os
import json
import CGData.Soft
from optparse import OptionParser


if __name__ == "__main__":
    
    parser = OptionParser()
    
    parser.add_option("-m", "--matrix", dest="matrix", default=None)
    parser.add_option("-c", "--clinical", action="store_true", dest="clinical", default=None)
    
    (options, args) = parser.parse_args()
    
    soft_file = args[0]
    soft = CGData.Soft.Soft(soft_file + ".sqlite")
    if not os.path.exists(soft_file + ".sqlite" ):
        handle = open(soft_file)
        soft.read(handle)
        handle.close()
    
    if options.matrix is not None:
        out = soft.build_matrix(options.matrix, 'ID_REF')
        out.store(soft_file + ".matrix")

    if options.clinical is not None:
        out = soft.build_clinical()
        out.store(soft_file + ".clinical_matrix")
