#!/usr/bin/env python

import sys
import CGData

if __name__ == "__main__":
    matrix = CGData.load( sys.argv[1] )
    handle = open(sys.argv[2], "w")
    matrix.write_gct(handle)
    handle.close()
