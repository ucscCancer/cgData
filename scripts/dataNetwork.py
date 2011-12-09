#!/usr/bin/env python

import sys
import CGData
import CGData.DataSet



def matrixNetwork(c):
    linkSpace = {}
    for type in c.set_hash:
        if issubclass( CGData.get_type( type ), CGData.CGDataMatrixObject ):
            for name in c.set_hash[type]:
                current = "%s:%s" % (type,name)
                x_link = c.set_hash[type][name].get_x_namespace()
                y_link = c.set_hash[type][name].get_y_namespace()
                if x_link is not None:
                    if x_link not in linkSpace:
                        linkSpace[x_link] = {}
                    linkSpace[x_link][current] = True
                    print "%s x_link %s" % (current, x_link)
                if y_link is not None:
                    if y_link not in linkSpace:
                        linkSpace[y_link] = {}				
                    linkSpace[y_link][current] = True
                    print "%s y_link %s" % (current, y_link)
    
    for ns in linkSpace:
        s = linkSpace[ns].keys()
        for i in range(len(s)):
            for j in range(i+1, len(s)):
                print ns, s[i], s[j]


def dependancy_graph(c):
    for type in c:
        for a in c[type]:
            for field in c[type][a]:
                if field.startswith(":"):
                    print a, field, c[type][a][field]



c = CGData.DataSet.DataSet()
c.scan_dirs(sys.argv[1:])
dependancy_graph(c)
#linkSpace = matrixNetwork(c)

