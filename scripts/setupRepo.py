#!/usr/bin/env python


import sys
import cgData.repo


repo = cgData.repo.repo()

repo.scanDir( sys.argv[1] )

repo.writeDigest()

print repo.checkDigest()

repo.store()
#repo.write( sys.stdout )
