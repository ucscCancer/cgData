#!/bin/bash

if [ ! -e tcga_dag ]; then 
	mkdir tcga_dag
fi

if [ ! -e tcga_dag/tcga.uuid.tab ]; then
	 ./scripts/tcgaUUIDFetch.py > tcga_dag/tcga.uuid.tab
fi	 

if [ ! -e tcga_dag/tcga.barcode.dag ]; then 
	./scripts/tcgaIDDagFetch.py tcga_dag/tcga.barcode.dag
fi

if [ ! -e tcga_dag/tcga.aliquot.report ]; then 
	./scripts/tcgaAliquotReportFetch.py tcga_dag/tcga.aliquot.report
fi

cat tcga_dag/tcga.uuid.tab | awk '{if (length($4)) print $4}' | sort | uniq > tcga_dag/disease.list
export PYTHONPATH=`pwd`
for a in `cat tcga_dag/disease.list`; do 
	cat tcga_dag/tcga.aliquot.report | awk "{if (\$2 == \"$a\") print \$1}" | ./scripts/selectIDDAG.py tcga_dag/tcga.barcode.dag - > tcga_dag/$a.dag
	cat tcga_dag/tcga.uuid.tab | awk "{if (\$4 == \"$a\") { print \$1 \"\t\" \$2 \"\n\" \$3 \"\t\" \$2} }"  | awk '{ if (NF > 1) print $0 }' >> tcga_dag/$a.dag
done

