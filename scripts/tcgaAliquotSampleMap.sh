#!/bin/bash

# parse file that can be downloaded at
# http://tcga-data.nci.nih.gov/datareports/aliquotIdBreakdownReport.htm

cat aliquotIdBreakdownReport.txt | grep -v Aliquot | awk '{print $2 "\t" $1 }' > tcga.sampleMap
cat aliquotIdBreakdownReport.txt | grep -v Aliquot | awk '{print $3 $9 "\t" $2 }' >> tcga.sampleMap
