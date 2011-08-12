

#rpy2 is the R for Python library
#this is used to take advantage of the GEOquery library in R
from rpy2 import robjects

from tempfile import NamedTemporaryFile
import csv
import os
import json

class GEOQuery:

    def __init__(self):
        robjects.r('library(GEOquery)')
        robjects.r('library(rjson)')
    
    def get_gsm(self, gsm_id):
        robjects.r.assign("gsm.id", gsm_id)
        tmp = NamedTemporaryFile(delete=True)
        tmp.close()
        robjects.r.assign("gsm.file", tmp.name)
        
        robjects.r('gsm <- getGEO(gsm.id)')
        robjects.r('write.table(Table(gsm), file = gsm.file, sep = "\t", row.names = FALSE, col.names = TRUE)')
        
        handle = open( tmp.name )
        reader = csv.reader( handle, delimiter="\t" )
        handle.close()
        os.unlink( tmp.name )
        
        robjects.r('cat(toJSON(Meta(gsm)), file = gsm.file)')
        handle = open( tmp.name )
        meta = json.loads( handle.read() )
        handle.close()
        
        print meta

        

#GSE24551
#http://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?mode=raw&is_datatable=true&acc=GPL5175&id=78&db=GeoDb_blob34
