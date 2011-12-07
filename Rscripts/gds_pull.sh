#!/bin/bash


for a in `cat gds.list`; do
	if [ ! -e tmp/GDS$a ]; then
		./getGEO.R GDS$a tmp/GDS$a
	fi
done
