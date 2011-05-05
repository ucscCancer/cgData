#!/bin/bash

srcDir=$1
dstDir=$2

if [ ! -e  $dstDir/AffyHuEx-1_0_st_hg18 ]; then
	probeMapBed12.py refGene_hg18.table $srcDir/AffyHuEx-1_0_st_hg18.bed12 > $dstDir/AffyHuEx-1_0_st_hg18
fi

if [ ! -e  $dstDir/affyU133Series_hg18 ]; then
	probeMapBed12.py refGene_hg18.table $srcDir/affyU133Series_hg18.bed12 > $dstDir/affyU133Series_hg18
fi

if [ ! -e  $dstDir/miRNA_hg18 ]; then
	probeMapBed12.py refGene_hg18.table $srcDir/miRNA_hg18.bed12 > $dstDir/miRNA_hg18
fi

if [ ! -e  $dstDir/H-miRNA_8x15K_GPL8617_hg18 ]; then
	probeMapBed12.py refGene_hg18.table $srcDir/H-miRNA_8x15K_GPL8617_hg18.bed12 > $dstDir/H-miRNA_8x15K_GPL8617_hg18
fi

if [ ! -e  $dstDir/affyU133U133Plus2_hg18 ]; then
	probeMapBed12.py refGene_hg18.table $srcDir/affyU133U133Plus2_hg18.bed12 > $dstDir/affyU133U133Plus2_hg18
fi

if [ ! -e  $dstDir/agilent_Human1AWholeGenome_hg18 ]; then
	probeMapBed12.py refGene_hg18.table $srcDir/agilent_Human1AWholeGenome_hg18.bed12 > $dstDir/agilent_Human1AWholeGenome_hg18
fi

if [ ! -e  $dstDir/H-miRNA_8x15Kv2_GPL8936_hg18 ]; then
	probeMapBed12.py refGene_hg18.table $srcDir/H-miRNA_8x15Kv2_GPL8936_hg18.bed12 > $dstDir/H-miRNA_8x15Kv2_GPL8936_hg18
fi

if [ ! -e  $dstDir/affyU133_hg18 ]; then
	probeMapBed12.py refGene_hg18.table $srcDir/affyU133_hg18.bed12 > $dstDir/affyU133_hg18
fi

if [ ! -e  $dstDir/hugoInProgress_hg18 ]; then
	probeMapBed12.py refGene_hg18.table $srcDir/hugoInProgress_hg18.bed12 > $dstDir/hugoInProgress_hg18
fi

if [ ! -e  $dstDir/affyU133Plus2_hg18 ]; then
	probeMapBed12.py refGene_hg18.table $srcDir/affyU133Plus2_hg18.bed12 > $dstDir/affyU133Plus2_hg18
fi

if [ ! -e  $dstDir/agilentG4112F_GPL6480_hg18 ]; then
	probeMapBed12.py refGene_hg18.table $srcDir/agilentG4112F_GPL6480_hg18.bed12 > $dstDir/agilentG4112F_GPL6480_hg18
fi

if [ ! -e  $dstDir/illuminaMethylation27K ]; then
	probeMapBed12.py -m refGene_hg18.table $srcDir/illuminaMethylation27K.bed12 > $dstDir/illuminaMethylation27K
fi

