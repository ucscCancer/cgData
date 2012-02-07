#!/usr/bin/env python

import sys
import os
import json
import CGData.Soft

if __name__ == "__main__":
    soft = CGData.Soft.Soft(sys.argv[1] + ".sqlite")
    if not os.path.exists( sys.argv[1] + ".sqlite" ):
        handle = open(sys.argv[1])
        soft.read(handle)
        handle.close()
    
    samples = list(soft.get_section_list("SAMPLE"))
    for sam in samples:
        cols =  list(soft.get_col_list(sam))
        if len(cols):
            print sam, cols
        else:
            print sam
        
