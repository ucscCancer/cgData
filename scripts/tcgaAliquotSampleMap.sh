#!/bin/bash

# parse file that can be downloaded at
# http://tcga-data.nci.nih.gov/datareports/aliquotIdBreakdownReport.htm

# http://tcga-data.nci.nih.gov/datareports/aliquotIdBreakdownExport.htm?exportType=tab&dir=undefined&sort=undefined&cols=aliquotId,analyteId,sampleId,participantId&filterReq={%22aliquotId%22:%22%22,%22analyteId%22:%22%22,%22sampleId%22:%22%22,%22participantId%22:%22%22}&formFilter=null

cat aliquotIdBreakdownReport.txt | grep -v Aliquot | awk '{print $2 "\t" $1 }' > tcga.sampleMap
cat aliquotIdBreakdownReport.txt | grep -v Aliquot | awk '{print $3 $9 "\t" $2 }' >> tcga.sampleMap
