#!/bin/bash

curl -O http://hgdownload.cse.ucsc.edu/goldenPath/hg18/database/refGene.txt.gz
gunzip -c refGene.txt.gz > refGene_hg18.txt
