
from xml.dom.minidom import parseString
import urllib
import urllib2
import os
import csv


host = "http://tcga-data.nci.nih.gov"
shost = "https://tcga-data.nci.nih.gov"


class dccwsItem(object):
    baseURL = "http://tcga-data.nci.nih.gov/tcgadccws/GetXML?query="

    def __init__(self):
        self.url = None

    def __iter__(self):
        next = self.url
        while next != None:
            data = urllib.urlopen(next).read()
            dom = parseString(data)
            # there might not be any archives for a dataset
            if len(dom.getElementsByTagName('queryResponse')) > 0:
                response = dom.getElementsByTagName('queryResponse').pop()
                classList = response.getElementsByTagName('class')
                for cls in classList:
                    className = cls.getAttribute("recordNumber")
                    outData = {}
                    #aObj = Archive()
                    for node in cls.childNodes:
                        nodeName = node.getAttribute("name")
                        if node.hasAttribute("xlink:href"):
                            outData[nodeName] =
                            node.getAttribute("xlink:href")
                        else:
                            outData[nodeName] =
                            getText(node.childNodes)
                    yield outData
            if len(dom.getElementsByTagName('next')) > 0:
                nextElm = dom.getElementsByTagName('next').pop()
                next = nextElm.getAttribute('xlink:href')
            else:
                next = None


class DiseaseList(dccwsItem):
    def __init__(self):
        super(DiseaseList, self).__init__()
        self.url = dccwsItem.baseURL + "Disease"


class ArchiveList(dccwsItem):
    def __init__(self):
        super(ArchiveList, self).__init__()
        self.url = dccwsItem.baseURL + "Archive"


class ArchiveCollection(dccwsItem):
    def __init__(self, diseaseID):
        super(ArchiveCollection, self).__init__()
        self.url = dccwsItem.baseURL +
        "Archive&Disease[@id=%s]&roleName=archiveCollection" % (diseaseID)


class Platform(dccwsItem):
    def __init__(self, archiveID):
        super(Platform, self).__init__()
        self.url = dccwsItem.baseURL +
        "Platform&Archive[@id=%s]&roleName=platform" % (archiveID)


class ArchiveType(dccwsItem):
    def __init__(self, archiveID):
        super(ArchiveType, self).__init__()
        self.url = dccwsItem.baseURL +
        "ArchiveType&Archive[@id=%s]&roleName=archiveType" % (archiveID)


class FileInfo(dccwsItem):
    def __init__(self, archiveID):
        super(FileInfo, self).__init__()
        self.url = dccwsItem.baseURL +
        "FileInfo&Archive[@id=%s]&roleName=fileCollection" % (archiveID)


class FileBarcode(dccwsItem):
    def __init__(self, fileID):
        super(FileBarcode, self).__init__()
        self.url = dccwsItem.baseURL +
        "BiospecimenBarcode&FileInfo[@id=%s]&roleName=biospecimenBarcodeCollection" % (fileID)


class CustomQuery(dccwsItem):
    def __init__(self, query):
        super(CustomQuery, self).__init__()
        self.url = dccwsItem.baseURL + query


def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)


skipFiles = [
    "MANIFEST.txt",
    "CHANGES_DCC.txt",
    "README_DCC.txt",
    "DESCRIPTION.txt",
    "README_HIPAA_AGES",
    "DCC_ALTERED_FILES.txt"
]

commonMap = {
 "Segment_Mean": "seg.mean",
 "Start": "loc.start",
 "End": "loc.end",
 "Chromosome": "chrom"
}


def allowedFile(name):
    if name.startswith("README") or name.endswith(".xml"):
        return False
    if name.endswith(".xsd") or name in skipFiles:
        return False
    if name.endswith(".loh.txt") or name.endswith(".segnormal.txt") or name.endswith(".FIRMA.txt"):
        return False
    return True


def extractGenetic(path, iHandle, oHandle):
    if allowedFile(os.path.basename(path)):
        if path.endswith('.idf.txt') or path.endswith('.sdrf.txt'):
            if path.endswith('.sdrf.txt'):
                read = csv.reader(iHandle, delimiter="\t")
                colNum = None
                for row in read:
                    if colNum is None:
                        colNum = {}
                        for i in range(len(row)):
                            colNum[row[i]] = i
                    else:
                        if not "Material Type" in colNum or row[colNum["Material Type"]] != "genomic_DNA":
                            oHandle.emit(row[colNum["Hybridization Name"]], row[colNum["Extract Name"]], "targets")
        else:
            mode = None
            target = None
            colName = None
            colType = None
            for line in iHandle:
                if colName is None:
                    colName = line.rstrip().split("\t")
                    if colName[0] == "Chromosome":
                        mode = 1
                        target = os.path.basename(path).split('.')[0]
                    if colName[0] == "Hybridization REF":
                        mode = 2

                    for i in range(len(colName)):
                        if colName[i] in commonMap:
                            colName[i] = commonMap[colName[i]]
                elif mode == 2 and colType is None:
                    colType = line.rstrip().split("\t")
                    for i in range(len(colType)):
                        if colType[i] in commonMap:
                            colType[i] = commonMap[colType[i]]
                else:
                    tmp = line.rstrip().split("\t")
                    if mode == 2:
                        out = {}
                        for col in colName[1:]:
                            out[col] = {"target": col}
                        for i in range(1, len(colType)):
                            out[colName[i]][colType[i]] = tmp[i]
                        for col in out:
                            oHandle.emit(tmp[0], out[col], path)
                    else:
                        out = {}
                        for i in range(len(colName)):
                            out[colName[i]] = tmp[i]
                        if mode == 1:
                            oHandle.emit(target, out, "probes")
                        else:
                            oHandle.emit(tmp[0], out, "probes")
