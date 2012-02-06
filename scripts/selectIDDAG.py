#!/usr/bin/env python

import sys
import CGData


def scan_children(node, iddag, out):
	for child in iddag.get_children(node):
		scan_children(child, iddag, out)
		out.write("%s\t%s\n" % (node, child))

def scan_parents(node, iddag, out):
	for parent in iddag.get_parents(node):
		scan_parents(parent, iddag, out)
		out.write("%s\t%s\n" % (parent, node))


if __name__ == "__main__":
	iddag = CGData.load(sys.argv[1])
	
	if sys.argv[2] == "-":
		handle = sys.stdin
	else:
		handle = open(sys.argv[2])
	
	
	for line in handle:
		name = line.rstrip()
		
		scan_children(name, iddag, sys.stdout)
		scan_parents(name, iddag, sys.stdout)
