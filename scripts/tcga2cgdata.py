#!/usr/bin/env python


from xml.dom.minidom import parseString
import urllib
import urllib2
import os
import csv
import sys
import tempfile
import re
import copy
import json
import datetime
import subprocess
from glob import glob
import shutil
import subprocess
from optparse import OptionParser


tcgaConfig = {
    'AgilentG4502A_07': {':dataSubType': 'geneExp',
                            ':probeMap': 'hugo',
                            ':sampleMap': 'tcga',
                            'dataType': 'genomicMatrix',
                            'probeField': 'log2 lowess normalized (cy5/cy3) collapsed by gene symbol'},
    'AgilentG4502A_07_1': {':dataSubType': 'geneExp',
                            ':probeMap': 'hugo',
                            ':sampleMap': 'tcga',
                            'dataType': 'genomicMatrix',
                            'probeField': 'log2 lowess normalized (cy5/cy3) collapsed by gene symbol'},
     'AgilentG4502A_07_2': {':dataSubType': 'geneExp',
                            ':probeMap': 'hugo',
                            ':sampleMap': 'tcga',
                            'dataType': 'genomicMatrix',
                            'probeField': 'log2 lowess normalized (cy5/cy3) collapsed by gene symbol'},
     'AgilentG4502A_07_3': {':dataSubType': 'geneExp',
                            ':probeMap': 'hugo',
                            ':sampleMap': 'tcga',
                            'dataType': 'genomicMatrix',
                            'probeField': 'log2 lowess normalized (cy5/cy3) collapsed by gene symbol'},
     'CGH-1x1M_G4447A': {':dataSubType': 'cna',
                         ':sampleMap': 'tcga',
                         'dataType': 'genomicSegment',
                         'probeField': 'seg.mean'},
     'Genome_Wide_SNP_6': {':assembly': 'hg18',
                           ':dataSubType': 'cna',
                           ':sampleMap': 'tcga',
                           'dataType': 'genomicSegment',
                           'probeField': 'seg.mean'},
     'H-miRNA_8x15K': {':dataSubType': 'miRNAExp',
                       ':probeMap': 'agilentHumanMiRNA',
                       ':sampleMap': 'tcga',
                       'dataType': 'genomicMatrix',
                       'probeField': 'unc_DWD_Batch_adjusted'},
     'H-miRNA_8x15Kv2': {':dataSubType': 'miRNAExp',
                         ':probeMap': 'agilentHumanMiRNA',
                         ':sampleMap': 'tcga',
                         'dataType': 'genomicMatrix',
                         'probeField': 'unc_DWD_Batch_adjusted'},
     'HG-CGH-244A': {':dataSubType': 'cna',
                     ':sampleMap': 'tcga',
                     'dataType': 'genomicSegment',
                     'probeField': 'Segment_Mean'},
     'HG-CGH-415K_G4124A': {':dataSubType': 'cna',
                            ':sampleMap': 'tcga',
                            'chromeField': 'Chromosome',
                            'dataType': 'genomicSegment',
                            'endField': 'End',
                            'probeField': 'Segment_Mean',
                            'startField': 'Start'},
     'HT_HG-U133A': {':dataSubType': 'geneExp',
                     ':probeMap': 'affyU133a',
                     ':sampleMap': 'tcga',
                     'dataType': 'genomicMatrix',
                     'probeField': 'Signal'},
     'HuEx-1_0-st-v2': {':dataSubType': 'miRNAExp',
                        ':probeMap': 'hugo',
                        ':sampleMap': 'tcga',
                        'dataType': 'genomicMatrix',
                        'probeField': 'Signal'},
     'Human1MDuo': {':dataSubType': 'cna',
                    ':sampleMap': 'tcga',
                    'dataType': 'genomicSegment',
                    'probeField': 'mean'},
     'HumanHap550': {':dataSubType': 'cna',
                     ':sampleMap': 'tcga',
                     'dataType': 'genomicSegment',
                     'probeField': 'mean'},
     'HumanMethylation27': {':dataSubType': 'DNAMethylation',
                            ':probeMap': 'illuminaHumanMethylation27',
                            ':sampleMap': 'tcga',
                            'dataType': 'genomicMatrix',
                            'probeField': 'Beta_Value'},
     'HumanMethylation450': {':dataSubType': 'DNAMethylation',
                             ':probeMap': 'illuminaHumanMethylation450',
                             ':sampleMap': 'tcga',
                             'dataType': 'genomicMatrix',
                             'probeField': 'Beta_Value'},
     'IlluminaHiSeq_RNASeq': {':sampleMap': 'tcga',
                              'datasubType': 'geneExp',
                              'fileFilter': '^.*annotated.gene.quantification.txt$|^.*sdrf.txt$',
                              'probeField': 'RPKM'}
}



class dccwsItem(object):
    baseURL = "http://tcga-data.nci.nih.gov/tcgadccws/GetXML?query="

    def __init__(self):
        self.url = None
            
    def __iter__(self):
        next = self.url        
        while next != None:
            handle = urllib.urlopen(next)
            data = handle.read()
            handle.close()
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
                            outData[ nodeName ] = node.getAttribute("xlink:href")            
                        else:
                            outData[ nodeName ] = getText( node.childNodes )
                    yield outData
            if len( dom.getElementsByTagName('next') ) > 0:
                nextElm = dom.getElementsByTagName('next').pop()
                next = nextElm.getAttribute( 'xlink:href' )
            else:
                next = None


class CustomQuery(dccwsItem):
    def __init__(self, query):
        super(CustomQuery, self).__init__()
        if query.startswith("http://"):
            self.url = query
        else:
            self.url = dccwsItem.baseURL + query

    
def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)
    

commonMap = {
    "Segment_Mean" : "seg.mean",
    "Start" : "loc.start",
    "End" : "loc.end",
    "Chromosome" : "chrom"
}


class TCGAFileScan:
    def __init__(self, path, outbase):
        self.path = path
        self.outbase = outbase
        self.out = {}
    
    def run(self):
        """
        This function takes a TCGA level 3 genetic file (file name and input handle),
        and tries to extract probe levels or target mappings (experimental ID to TCGA barcode)
        it emits these values to a handle, using the 'targets' and 'probes' string to identify 
        the type of data being emited
        """
        iHandle = open(self.path)
        if self.path.endswith( '.idf.txt' ) or self.path.endswith( '.sdrf.txt' ):
            if self.path.endswith( '.sdrf.txt' ):
                read = csv.reader( iHandle, delimiter="\t" )
                colNum = None
                for row in read:
                    if colNum is None:
                        colNum = {}
                        for i in range(len(row)):
                            colNum[ row[i] ] = i
                    else:
                        if not colNum.has_key("Material Type") or ( not row[ colNum[ "Material Type" ] ] in [ "genomic_DNA", "total_RNA" ] ):
                            try:
                                if colNum.has_key( "Derived Array Data File" ):
                                    self.emit( row[ colNum[ "Derived Array Data File" ] ].split('.')[0], row[ colNum[ "Extract Name" ] ], "targets" )
                                    self.emit( row[ colNum[ "Derived Array Data File" ] ], row[ colNum[ "Extract Name" ] ], "targets" )
                                elif colNum.has_key( "Derived Data File"):
                                    self.emit( row[ colNum[ "Derived Data File" ] ].split('.')[0], row[ colNum[ "Extract Name" ] ], "targets" )  
                                    self.emit( row[ colNum[ "Derived Data File" ] ], row[ colNum[ "Extract Name" ] ], "targets" )    
                                else:
                                    self.emit( row[ colNum[ "Hybridization Name" ] ] , row[ colNum[ "Extract Name" ] ], "targets" )
                            except IndexError:
                                pass #there can be blank lines in the SDRF
        else:
            mode = None
            #modes
            #1 - segmentFile - one sample per file/no sample info inside file
            #2 - two col header matrix file
            #3 - segmentFile - sample information inside file
            target = None
            colName = None
            colType = None
            for line in iHandle:
                if colName is None:
                    colName = line.rstrip().split("\t")                     
                    if colName[0] == "Hybridization REF":
                        mode=2
                    elif colName[0] == "Chromosome":
                        mode=1
                        target=os.path.basename( self.path ).split('.')[0] #seg files are named by the filename before the '.' extention
                    elif colName[1] == "chrom":
                        mode = 3
                        target=os.path.basename( self.path ).split('.')[0] #seg files are named by the filename before the '.' extention
                        
                    for i in range(len(colName)):
                        if commonMap.has_key( colName[i] ):
                            colName[i] = commonMap[ colName[i] ]
                elif mode==2 and colType is None:
                    colType=line.rstrip().split("\t")
                    for i in range(len(colType)):
                        if commonMap.has_key( colType[i] ):
                            colType[i] = commonMap[ colType[i] ]
                else:
                    tmp = line.rstrip().split("\t")
                    if mode == 2:
                        out={}
                        for col in colName[1:]:
                            out[ col ] = { "target" : col }
                        for i in range(1,len(colType)):
                            try:
                                out[ colName[i] ][ colType[i] ] = tmp[i]
                            except IndexError:
                                out[ colName[i] ][ colType[i] ] = "NA"
                        for col in out:
                            self.emit( tmp[0], out[col], "probes" )
                    else:
                        out = {}
                        for i in range(len(colName)):
                            out[ colName[i] ] = tmp[i]
                        out['file'] = os.path.basename(self.path)
                        if mode==1:
                            self.emit( target, out, "segments" )
                        elif mode == 3:
                            self.emit( tmp[0], out, "segments" )
                        else:
                            self.emit( tmp[0], out, "probes" )

        for a in self.out:
            self.out[a].close()

    def emit(self, key, data, port):
        if port not in self.out:
            self.out[port] = open(self.outbase + "." + port, "w")
        self.out[port].write( "%s\t%s\n" % (key, json.dumps(data)))

class TarballExtract:

    excludes = [
         "MANIFEST.txt",
         "CHANGES_DCC.txt",
         "README_DCC.txt",
         "DESCRIPTION.txt",
         "DCC_ALTERED_FILES.txt", 
         r'.wig$'
    ]


    def __init__(self, path, config, workdir):
        self.path = path
        self.config = config
        self.workdir = workdir
    
    def run(self):
        filter = None
        if not os.path.exists(self.workdir):
            os.makedirs(self.workdir)
        dir = tempfile.mkdtemp(dir=self.workdir)
        if "fileFilter" in self.config:
            filter = re.compile(self.config["filter"])
        print "Extract to ", self.workdir
        os.system("tar xvzf %s -C %s > /dev/null" % (self.path, dir))
        self.inc = 0
        self.scandirs(dir, filter)
        #shutil.rmtree(dir)

    def checkExclude( self, name ):
        for e in self.excludes:
            if re.search( e, name ):
                return True
        return False
    
    def scandirs(self, path, filter=None):
        if os.path.isdir(path):
            for a in glob(os.path.join(path, "*")):
                self.scandirs(a, filter)
        else:
            name = os.path.basename(path)
            if not self.checkExclude(name):
                if filter is None or filter.match(name):
                    dateStr = datetime.date.today().isoformat()
                    outPath = "%s/%s.%d" % (self.workdir, os.path.basename(self.path), self.inc)
                    print "Scanning ", outPath, path
                    scan = TCGAFileScan(path, outPath)
                    scan.run()
                    self.inc += 1

class TableReader:
    def __init__(self, path):
        self.path = path
    
    def __iter__(self):
        if self.path is not None and os.path.exists(self.path):
            handle = open(self.path)
            for line in handle:
                tmp = line.rstrip().split("\t")
                yield tmp[0], json.loads(tmp[1])
            handle.close()


class CGDataCompile:
    def __init__(self, segmentPath, probePath, targetPath, config):
        self.segmentPath = segmentPath
        self.probePath = probePath
        self.targetPath = targetPath
        self.config = config
        
    
    def run(self):
        #use the target table to create a name translation table
        #also setup target name enumeration, so they will have columns
        #numbers
        
        handles = {}
        handles[ "geneticExtract:targets" ] = TableReader(self.targetPath)
        handles[ "geneticExtract:probes" ] = TableReader(self.probePath)
        handles[ "geneticExtract:segments" ] = TableReader(self.segmentPath)


        tHandle = handles["geneticExtract:targets"]
        tEnum = {}
        tTrans = {}
        for key, value in tHandle:
            if not tEnum.has_key( value ):
                tEnum[ value ] = len( tEnum )
            tTrans[ key ] = value
                
        matrixFile = None
        segFile = None

        curName = None
        curData = {}
        missingCount = 0
        pHandle = handles["geneticExtract:probes"]
        for key, value in pHandle:
            if matrixFile is None:
                matrixFile = open( "%s/matrix_file" % (self.config['workdir']), "w" )            
                out = ["NA"] * len(tEnum)
                for target in tEnum:
                    out[ tEnum[ target ] ] = target
                matrixFile.write( "%s\t%s\n" % ( "#probe", "\t".join( out ) ) )        
                probeField = self.config['probeField']
            
            if curName != key:
                if curName is not None:
                    out = ["NA"] * len(tEnum)
                    for target in curData:
                        out[ tEnum[ tTrans[ target ] ] ] = str( curData[ target ] )
                    matrixFile.write( "%s\t%s\n" % ( curName, "\t".join( out ) ) )                
                curName = key
                curData = {}
            if "target" in value:
                curData[ value[ "target" ] ] = value[ probeField ]
            elif "file" in value:
                curData[ value[ "file" ] ] = value[ probeField ]
                
            
        if matrixFile is not None:
            matrixFile.close()
            matrixName = self.config["baseName"]    
            matrixInfo = { 'type' : 'genomicMatrix', 'name' : matrixName, 'dataProducer' : 'Remus TCGA Import', "accessMap" : "public", "redistribution" : "yes" }
            for key in [ ':probeMap', ':dataSubType', ':sampleMap' ]:
                matrixInfo[ key ] = self.config[key]    
            self.emitFile( os.path.join(config['outdir'], matrixName), matrixInfo, "%s/matrix_file"  % (self.config['workdir']) )


        startField  = "loc.start"
        endField    = "loc.end"
        valField    = "seg.mean"
        chromeField = "chrom"
        
        segFile = None
        sHandle = handles["geneticExtract:segments"]
        for key, value in sHandle:
            if segFile is None:
                segFile = open("%s/segment_file"  % (self.config['workdir']), "w")
            curName = tTrans[key] # "-".join( tTrans[ key ].split('-')[0:4] )
            segFile.write( "%s\tchr%s\t%s\t%s\t.\t%s\n" % ( curName, value[ chromeField ], int(value[ startField ])+1, value[ endField ], value[ valField ] ) )

        if segFile is not None:
            segFile.close()
            matrixName = self.config["baseName"]
            matrixInfo = { 'type' : 'genomicSegment', 'name' : matrixName, 'dataProducer' : 'Remus TCGA Import', "accessMap" : "public", "redistribution" : "yes" }
            for key in [ ':dataSubType', ':sampleMap' ]:
                matrixInfo[ key ] = self.config[key]
            self.emitFile( os.path.join(config['outdir'], matrixName), matrixInfo, "%s/segment_file"  % (self.config['workdir']) )        

    def emitFile(self, name, meta, file):
        mHandle = open(name + ".json", "w")
        mHandle.write( json.dumps(meta))
        mHandle.close()
        shutil.copyfile(file, name)
    

if __name__ == "__main__":
    
    parser = OptionParser()
    #Stack.addJobTreeOptions(parser) 
    
    parser.add_option("-l", "--platform-list", dest="platform_list", action="store_true", help="Get list of platforms", default=False)
    parser.add_option("-p", "--platform", dest="platform", help="Platform Selection", default=None)
    parser.add_option("-f", "--filelist", dest="filelist", help="List files needed to convert TCGA project basename into cgData", default=None)
    parser.add_option("-b", "--basename", dest="basename", help="Convert TCGA project basename into cgData", default=None)
    parser.add_option("-m", "--mirror", dest="mirror", help="Mirror Location", default=None)
    parser.add_option("-w", "--workdir", dest="workdir", help="Working directory", default="tmp")
    parser.add_option("-o", "--out-dir", dest="outdir", help="Working directory", default="./")
    parser.add_option("-c", "--cancer", dest="cancer", help="List Archives by cancer type", default=None)
    parser.add_option("-d", "--download", dest="download", help="Download files for archive", default=None)
    
    
    options, args = parser.parse_args()
    
    if options.platform_list:
        q = CustomQuery("Platform")
        for e in q:
            print e['name']
    
    if options.platform:
        q = CustomQuery("Archive[Platform[@name=%s]][@isLatest=1]" % options.platform)
        out = {}
        for e in q:
            name = e['baseName']
            if name not in out:
                print name
                out[name] = True

    if options.cancer is not None:
        q = CustomQuery("Archive[@isLatest=1][Disease[@abbreviation=%s]]" % (options.cancer))
        out = {}
        for e in q:
            name = e['baseName']
            if name not in out:
                print name
                out[name] = True

    if options.filelist:
        q = CustomQuery("Archive[@baseName=%s][@isLatest=1][ArchiveType[@type=Level_3]]" % (options.filelist))
        for e in q:
            print e['deployLocation']
        q = CustomQuery("Archive[@baseName=%s][@isLatest=1][ArchiveType[@type=mage-tab]]" % (options.filelist))
        for e in q:
            print e['deployLocation']

    if options.download is not None:
        if options.mirror is None:
            print "Define mirror location"
            sys.exit(1)
        q = CustomQuery("Archive[@baseName=%s][@isLatest=1][ArchiveType[@type=Level_3]]" % (options.download))
        urls = []
        for e in q:
            urls.append( e['deployLocation'] )
            urls.append( e['deployLocation'] + ".md5" )
            
        q = CustomQuery("Archive[@baseName=%s][@isLatest=1][ArchiveType[@type=mage-tab]]" % (options.download))
        for e in q:
            urls.append( e['deployLocation'] )
            urls.append( e['deployLocation'] + ".md5" )
        
        for url in urls:
            src = "http://tcga-data.nci.nih.gov/" + url
            dst = os.path.join(options.mirror, re.sub("^/", "", url))
            dir = os.path.dirname(dst)
            if not os.path.exists(dir):
                print "mkdir", dir
                os.makedirs(dir)
            if not os.path.exists( dst ):
                print "download %s to %s" % (src, dst)
                urllib.urlretrieve(src, dst)

    if options.basename:
        if options.mirror is None:
            print "Need mirror location"
            sys.exit(1)

        dates = []
        q = CustomQuery("Archive[@baseName=%s][@isLatest=1][ArchiveType[@type=Level_3]]" % (options.basename))
        urls = {}
        for e in q:
            dates.append( datetime.datetime.strptime( e['addedDate'], "%m-%d-%Y" ) )
            q2 = CustomQuery(e['platform'])
            platform = None
            for e2 in q2:
                print e2
                platform = e2['alias']
            urls[ options.mirror + e['deployLocation'] ] = platform

        q = CustomQuery("Archive[@baseName=%s][@isLatest=1][ArchiveType[@type=mage-tab]]" % (options.basename))
        for e in q:
            dates.append( datetime.datetime.strptime( e['addedDate'], "%m-%d-%Y" ) )
            q2 = CustomQuery(e['platform'])
            platform = None
            for e2 in q2:
                print e2
                platform = e2['alias']
            urls[ options.mirror + e['deployLocation'] ] = platform

        dates.sort()
        dates.reverse()
        nameSuffix = dates[0].strftime( "%Y%m%d" )

        
        for f in urls:
            if not os.path.exists(f):
                print "Missing file %s" % (f)
                sys.exit(1)
        config = None
        for f in urls:
            if config is None:
                config = copy.deepcopy(tcgaConfig[urls[f]])
            t = TarballExtract(f, config, options.workdir )
            t.run()
        
        subprocess.call("cat %s/*.segments | sort -k 1 > %s/segments" % (options.workdir, options.workdir), shell=True)
        subprocess.call("cat %s/*.probes | sort -k 1 > %s/probes" % (options.workdir, options.workdir), shell=True)
        subprocess.call("cat %s/*.targets | sort -k 1 > %s/targets" % (options.workdir, options.workdir), shell=True)
        
        config['baseName'] = options.basename + "_" + nameSuffix
        config['workdir'] = options.workdir
        config['outdir'] = options.outdir
        comp = CGDataCompile( "%s/segments" % (options.workdir), "%s/probes" % (options.workdir), "%s/targets" % (options.workdir), config)
        comp.run()
