
from xml.dom.minidom import parseString
import urllib
import urllib2
import os
import csv


HOST = "http://tcga-data.nci.nih.gov"
SHOST = "https://tcga-data.nci.nih.gov"


class DCCWSItem(object):
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
                            outData[nodeName] = node.getAttribute("xlink:href")
                        else:
                            outData[nodeName] = getText(node.childNodes)
                    yield outData
            if len(dom.getElementsByTagName('next')) > 0:
                nextElm = dom.getElementsByTagName('next').pop()
                next = nextElm.getAttribute('xlink:href')
            else:
                next = None


class DiseaseList(DCCWSItem):
    def __init__(self):
        super(DiseaseList, self).__init__()
        self.url = DCCWSItem.baseURL + "Disease"


class ArchiveList(DCCWSItem):
    def __init__(self):
        super(ArchiveList, self).__init__()
        self.url = DCCWSItem.baseURL + "Archive"


class ArchiveCollection(DCCWSItem):
    def __init__(self, diseaseID):
        super(ArchiveCollection, self).__init__()
        self.url = DCCWSItem.baseURL + "Archive&Disease[@id=%s]&roleName=archiveCollection" % (diseaseID)


class Platform(DCCWSItem):
    def __init__(self, archiveID):
        super(Platform, self).__init__()
        self.url = DCCWSItem.baseURL + "Platform&Archive[@id=%s]&roleName=platform" % (archiveID)


class ArchiveType(DCCWSItem):
    def __init__(self, archiveID):
        super(ArchiveType, self).__init__()
        self.url = DCCWSItem.baseURL + "ArchiveType&Archive[@id=%s]&roleName=archiveType" % (archiveID)


class FileInfo(DCCWSItem):
    def __init__(self, archiveID):
        super(FileInfo, self).__init__()
        self.url = DCCWSItem.baseURL + "FileInfo&Archive[@id=%s]&roleName=fileCollection" % (archiveID)


class FileBarcode(DCCWSItem):
    def __init__(self, fileID):
        super(FileBarcode, self).__init__()
        self.url = DCCWSItem.baseURL + "BiospecimenBarcode&FileInfo[@id=%s]&roleName=biospecimenBarcodeCollection" % (fileID)


class CustomQuery(DCCWSItem):
    def __init__(self, query):
        super(CustomQuery, self).__init__()
        self.url = DCCWSItem.baseURL + query


def get_text(nodelist):
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

common_map = {
 "Segment_Mean": "seg.mean",
 "Start": "loc.start",
 "End": "loc.end",
 "Chromosome": "chrom"
}


def allowed_file(name):
    if name.startswith("README") or name.endswith(".xml"):
        return False
    if name.endswith(".xsd") or name in skipFiles:
        return False
    if name.endswith(".loh.txt") or name.endswith(".segnormal.txt") or name.endswith(".FIRMA.txt"):
        return False
    return True


def extract_genetic(path, ihandle, ohandle):
    if allowed_file(os.path.basename(path)):
        if path.endswith('.idf.txt') or path.endswith('.sdrf.txt'):
            if path.endswith('.sdrf.txt'):
                read = csv.reader(ihandle, delimiter="\t")
                col_num = None
                for row in read:
                    if col_num is None:
                        col_num = {}
                        for i in range(len(row)):
                            col_num[row[i]] = i
                    else:
                        if not "Material Type" in col_num or row[col_num["Material Type"]] != "genomic_DNA":
                            ohandle.emit(row[col_num["Hybridization Name"]], row[col_num["Extract Name"]], "targets")
        else:
            mode = None
            target = None
            col_name = None
            col_type = None
            for line in ihandle:
                if col_name is None:
                    col_name = line.rstrip().split("\t")
                    if col_name[0] == "Chromosome":
                        mode = 1
                        target = os.path.basename(path).split('.')[0]
                    if col_name[0] == "Hybridization REF":
                        mode = 2

                    for i in range(len(col_name)):
                        if col_name[i] in common_map:
                            col_name[i] = common_map[col_name[i]]
                elif mode == 2 and col_type is None:
                    col_type = line.rstrip().split("\t")
                    for i in range(len(col_type)):
                        if col_type[i] in common_map:
                            col_type[i] = common_map[col_type[i]]
                else:
                    tmp = line.rstrip().split("\t")
                    if mode == 2:
                        out = {}
                        for col in col_name[1:]:
                            out[col] = {"target": col}
                        for i in range(1, len(col_type)):
                            out[col_name[i]][col_type[i]] = tmp[i]
                        for col in out:
                            ohandle.emit(tmp[0], out[col], path)
                    else:
                        out = {}
                        for i in range(len(col_name)):
                            out[col_name[i]] = tmp[i]
                        if mode == 1:
                            ohandle.emit(target, out, "probes")
                        else:
                            ohandle.emit(tmp[0], out, "probes")
