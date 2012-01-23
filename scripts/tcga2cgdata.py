#!/usr/bin/env python


"""
Script to scan and extract TCGA data and compile it into the cgData

Usage::
    
    tcga2cgdata.py [options]

Options::
    
      -h, --help            show this help message and exit
      -a, --platform-list   Get list of platforms
      -p PLATFORM, --platform=PLATFORM
                            Platform Selection
      -l, --supported       List Supported Platforms
      -f FILELIST, --filelist=FILELIST
                            List files needed to convert TCGA project basename
                            into cgData
      -b BASENAME, --basename=BASENAME
                            Convert TCGA project basename into cgData
      -m MIRROR, --mirror=MIRROR
                            Mirror Location
      -w WORKDIR_BASE, --workdir=WORKDIR_BASE
                            Working directory
      -o OUTDIR, --out-dir=OUTDIR
                            Working directory
      -c CANCER, --cancer=CANCER
                            List Archives by cancer type
      -d DOWNLOAD, --download=DOWNLOAD
                            Download files for archive
      -e LEVEL, --level=LEVEL
                            Data Level
      -s CHECKSUM, --check-sum=CHECKSUM
                            Check project md5
      -r, --sanitize        Remove race/ethnicity from clinical data


Example::
    
    ./scripts/tcga2cgdata.py -b intgen.org_KIRC_bio -m /inside/depot -e 1 -r -w tmp


"""

from xml.dom.minidom import parseString
import urllib
import urllib2
import os
import csv
import sys
import hashlib
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


class TCGAGeneticFileScan:
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


adminNS = "http://tcga.nci/bcr/xml/administration/2.3"

class TCGAClinialScan:
    
    def __init__(self, path, outbase):
        self.path = path
        self.outbase = outbase
        self.out = {}
   
   
    def run(self):
        handle = open(self.path)
        data = handle.read()
        handle.close()
        xml=parseString(data)
        self.parseXMLFile(xml)
        for a in self.out:
            self.out[a].close()
            
    def getText(self, nodelist):
        rc = []
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return ''.join(rc)


    def parseXMLFile(self, dom):    
        admin = {}
        for node in dom.getElementsByTagNameNS( adminNS, "admin"):
            for cNode in node.childNodes:
                if cNode.nodeType == cNode.ELEMENT_NODE:
                    admin[ cNode.localName ] = {}
                    admin[ cNode.localName ]['value'] = getText( cNode.childNodes )
        
        name = None
        patient = {}
        patientName = None
        for node in dom.childNodes[0].childNodes:
            if node.nodeType == node.ELEMENT_NODE:
                if node.localName == 'patient':
                    for elm in node.childNodes:
                        if elm.nodeType == elm.ELEMENT_NODE:
                            if ( elm.localName == 'bcr_patient_barcode' ):
                                name = getText( elm.childNodes )
                                patientName = name
                            if ( elm.getAttribute( 'procurement_status' ) == "Completed" ):
                                patient[ elm.localName ] = {}
                                patient[ elm.localName ]['value'] = getText( elm.childNodes )
                                patient[ elm.localName ]['tier']  = elm.getAttribute( 'tier' )
                                patient[ elm.localName ]['precision'] = elm.getAttribute( 'precision' )
                                
        if name is not None:
            for key in admin:
                patient[ key ] = admin[ key ]
            self.emit( name, patient, "patient" )

        for node in dom.childNodes[0].childNodes:
            if node.nodeType == node.ELEMENT_NODE and node.localName == 'patient':
                for samples in node.childNodes:
                    if samples.nodeType == samples.ELEMENT_NODE and samples.localName == 'samples':                        
                        for sample in samples.childNodes:
                            if sample.nodeType == samples.ELEMENT_NODE and sample.localName == 'sample':
                                sampleData = {}
                                for value in sample.childNodes:
                                    if value.nodeType == value.ELEMENT_NODE:                                        
                                        if value.localName == 'bcr_sample_barcode' :
                                            name = getText( value.childNodes )
                                        if value.getAttribute( 'procurement_status' ) == "Completed" :
                                            sampleData[ value.localName ] = {}
                                            sampleData[ value.localName ]['value'] = getText( value.childNodes )
                                            
                                #patientName = re.sub( r'\-...$', "", name )
                                self.emit( name, sampleData, "sample" )
                                self.emit( name, patient, "sample")

                    if samples.nodeType == samples.ELEMENT_NODE and samples.localName == 'drugs':
                        for drug in samples.childNodes:
                            if drug.nodeType == samples.ELEMENT_NODE and drug.localName == 'drug':
                                drugData = {}
                                for value in drug.childNodes:
                                    if value.nodeType == value.ELEMENT_NODE:                                        
                                        if value.localName == 'bcr_drug_barcode' :
                                            name = getText( value.childNodes )
                                        if value.getAttribute( 'procurement_status' ) == "Completed" :
                                            drugData[ value.localName ] = {}
                                            drugData[ value.localName ]['value'] = getText( value.childNodes )
                                            
                                #patientName = re.sub( r'\-...$', "", name )
                                self.emit( patientName, drugData, "drug" )

                    if samples.nodeType == samples.ELEMENT_NODE and samples.localName == 'radiations':
                        for rad in samples.childNodes:
                            if rad.nodeType == samples.ELEMENT_NODE and rad.localName == 'radiation':
                                radData = {}
                                for value in rad.childNodes:
                                    if value.nodeType == value.ELEMENT_NODE:                                        
                                        if value.localName == 'bcr_radiation_barcode' :
                                            name = getText( value.childNodes )
                                        if value.getAttribute( 'procurement_status' ) == "Completed" :
                                            radData[ value.localName ] = {}
                                            radData[ value.localName ]['value'] = getText( value.childNodes )
                                            
                                #patientName = re.sub( r'\-...$', "", name )
                                self.emit( patientName, radData, "radiation" )

    def emit(self, key, data, port):
        if port not in self.out:
            self.out[port] = open(self.outbase + "." + port, "w")
        self.out[port].write( "%s\t%s\n" % (key, json.dumps(data)))


class TarballExtract:

    excludes = [
         "MANIFEST.txt",
         "CHANGES_DCC.txt",
         "README_DCC.txt",
         "README.txt",
         "DESCRIPTIO",
         "DESCRIPTION.txt",
         "DCC_ALTERED_FILES.txt", 
         r'.wig$'
    ]


    def __init__(self, path, config, workdir):
        self.path = path
        self.config = config
        self.workdir = workdir
    
    def run(self):
        filterInclude = None
        filterExclude = None
        dir = tempfile.mkdtemp(dir=self.workdir)
        if "fileInclude" in self.config:
            filterInclude = re.compile(self.config["fileInclude"])
        if "fileExclude" in self.config:
            filterExclude = re.compile(self.config["fileExclude"])
        print "Extract to ", self.workdir
        os.system("tar xvzf %s -C %s > /dev/null" % (self.path, dir))
        self.inc = 0
        self.scandirs(dir, filterInclude, filterExclude)
        #shutil.rmtree(dir)

    def checkExclude( self, name ):
        for e in self.excludes:
            if re.search( e, name ):
                return True
        return False
    
    def scandirs(self, path, filterInclude=None, filterExclude=None):
        if os.path.isdir(path):
            for a in glob(os.path.join(path, "*")):
                self.scandirs(a, filterInclude, filterExclude)
        else:
            name = os.path.basename(path)
            if not self.checkExclude(name):
                if (filterInclude is None or filterInclude.match(name)) and (filterExclude is None or not filterExclude.match(name)):
                    dateStr = datetime.date.today().isoformat()
                    outPath = "%s/%s.%d" % (self.workdir, os.path.basename(self.path), self.inc)
                    print "Scanning ", outPath, path
                    scan = self.config['extract'](path, outPath)
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


class GeneticDataCompile:
    def __init__(self, workdir, config):
        self.workdir = workdir
        self.config = config
        self.errors = []
        
    
    def run(self):
        #use the target table to create a name translation table
        #also setup target name enumeration, so they will have columns
        #numbers
        
        
        subprocess.call("sort -k 1 %s/*.segments > %s/segments" % (self.workdir, self.workdir), shell=True)
        subprocess.call("sort -k 1 %s/*.probes > %s/probes" % (self.workdir, self.workdir), shell=True)
        subprocess.call("sort -k 1 %s/*.targets > %s/targets" % (self.workdir, self.workdir), shell=True)
                
        handles = {}
        handles[ "geneticExtract:targets" ] = TableReader(self.workdir + "/targets")
        handles[ "geneticExtract:probes" ] = TableReader(self.workdir + "/probes")
        handles[ "geneticExtract:segments" ] = TableReader(self.workdir + "/segments")


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
            matrixInfo = { 
                'cgdata' : {
                    'type' : 'genomicMatrix', 
                    'name' : matrixName, 
                },
                'dataProducer' : 'Remus TCGA Import', 
                "accessMap" : "public", 
                "redistribution" : "yes" 
            }
            matrixInfo['cgdata']['columnKeySrc'] = { "type" : "probe", "name" : self.conf[":probeMap"] }
            matrixInfo['cgdata']['rowKeySrc'] =    { "type" : "idDAG", "name" : 'tcga' }
            self.emitFile( os.path.join(self.config['outdir'], matrixName), matrixInfo, "%s/matrix_file"  % (self.config['workdir']) )


        startField  = "loc.start"
        endField    = "loc.end"
        valField    = "seg.mean"
        chromeField = "chrom"
        
        segFile = None
        sHandle = handles["geneticExtract:segments"]
        for key, value in sHandle:
            if segFile is None:
                segFile = open("%s/segment_file"  % (self.config['workdir']), "w")
            try:
                curName = tTrans[key] # "-".join( tTrans[ key ].split('-')[0:4] )
                segFile.write( "%s\tchr%s\t%s\t%s\t.\t%s\n" % ( curName, value[ chromeField ], int(value[ startField ])+1, value[ endField ], value[ valField ] ) )
            except KeyError:
                self.addError( "TargetInfo Not Found: %s" % (key))
        if segFile is not None:
            segFile.close()
            matrixName = self.config["baseName"]
            matrixInfo = { 'type' : 'genomicSegment', 'name' : matrixName, 'dataProducer' : 'Remus TCGA Import', "accessMap" : "public", "redistribution" : "yes" }
            for key in [ ':dataSubType', ':sampleMap' ]:
                matrixInfo[ key ] = self.config[key]
            self.emitFile( os.path.join(self.config['outdir'], matrixName), matrixInfo, "%s/segment_file"  % (self.config['workdir']) )        

    def emitFile(self, name, meta, file):
        mHandle = open(name + ".json", "w")
        mHandle.write( json.dumps(meta))
        mHandle.close()
        shutil.copyfile(file, name)
        if len(self.errors):
            eHandle = open( name + ".error", "w" )
            for msg in self.errors:
                eHandle.write( msg + "\n" )
            eHandle.close()
    
    def addError(self, msg):
        self.errors.append(msg)

class ClinicalDataCompile:
    def __init__(self, workdir, config):
        self.workdir = workdir
        self.config = config
    
    def run(self):
        matrixList = [ "patient", "sample", "radiation", "drug" ]
        for matrixName in matrixList:
            subprocess.call("cat %s/*.%s | sort -k 1 > %s/%s" % (self.workdir, matrixName, self.workdir, matrixName), shell=True)
            handle = TableReader(self.workdir + "/" + matrixName)
            matrix = {}
            colEnum = {}
            for key, value in handle:
                if key not in matrix:
                    matrix[key] = {}
                for col in value:
                    matrix[key][col] = value[col]
                    if col not in colEnum:
                        if not self.config['sanitize'] or col not in [ 'race', 'ethnicity' ]:
                            colEnum[col] = len(colEnum)
            
            outname = self.config["baseName"] + "_" + matrixName
            
            fileInfo = {
                "cgdata" : {
                    "type" : "clinicalMatrix",
                    "name" : outname,
                    "rowKeySrc" : {
                        "type" : "idDAG",
                        "name" : "tcga"
                    }
                }
            }
            handle = open( os.path.join(self.config['workdir'], matrixName + "_file"), "w")
            cols = [None] * (len(colEnum))
            for col in colEnum:
                cols[colEnum[col]] = col
            handle.write("sample\t%s\n" % ("\t".join(cols)))
            for key in matrix:
                cols = [""] * (len(colEnum))
                for col in colEnum:
                    if col in matrix[key]:
                        cols[colEnum[col]] = matrix[key][col]['value']
                handle.write("%s\t%s\n" % (key, "\t".join(cols)))
            handle.close()
            self.emitFile( os.path.join(self.config['outdir'], self.config["baseName"]  + "_" + outname), fileInfo, "%s/%s_file"  % (self.config['workdir'], matrixName) )        

    def emitFile(self, name, meta, file):
        mHandle = open(name + ".json", "w")
        mHandle.write( json.dumps(meta))
        mHandle.close()
        shutil.copyfile(file, name)
            


class TCGAExtract:
    
    def __init__(self, options):
        self.options = options
    
    def run(self):
        dates = []
        q = CustomQuery("Archive[@baseName=%s][@isLatest=1][ArchiveType[@type=Level_%s]]" % (self.options.basename, self.options.level))
        urls = {}
        for e in q:
            dates.append( datetime.datetime.strptime( e['addedDate'], "%m-%d-%Y" ) )
            q2 = CustomQuery(e['platform'])
            platform = None
            for e2 in q2:
                print e2
                platform = e2['alias']
            urls[ self.options.mirror + e['deployLocation'] ] = platform

        q = CustomQuery("Archive[@baseName=%s][@isLatest=1][ArchiveType[@type=mage-tab]]" % (self.options.basename))
        for e in q:
            dates.append( datetime.datetime.strptime( e['addedDate'], "%m-%d-%Y" ) )
            q2 = CustomQuery(e['platform'])
            platform = None
            for e2 in q2:
                print e2
                platform = e2['alias']
            urls[ self.options.mirror + e['deployLocation'] ] = platform

        if len(dates) == 0:
            print "No Files found"
            return
        dates.sort()
        dates.reverse()
        nameSuffix = dates[0].strftime( "%Y%m%d" )

        
        for f in urls:
            if not os.path.exists(f):
                print "Missing file %s" % (f)
                return
        config = None
        
        if not os.path.exists(self.options.workdir_base):
            os.makedirs(self.options.workdir_base)

        workdir = tempfile.mkdtemp(dir=self.options.workdir_base)
        
        for f in urls:
            if config is None:
                config = copy.deepcopy(tcgaConfig[urls[f]])
            t = TarballExtract(f, config, workdir )
            t.run()
                    
        
        config['baseName'] = self.options.basename + "_" + nameSuffix
        config['workdir'] = workdir
        config['outdir'] = self.options.outdir
        config['sanitize'] = self.options.sanitize
        
        comp = config['compile'](workdir, config)
        comp.run()
        
        shutil.rmtree(workdir)

           


class MyDownloader(urllib.FancyURLopener):
    def __init__(self):
        urllib.FancyURLopener.__init__(self)
        self.user = None
        self.password = None
        
    
    def prompt_user_passwd(self, host, realm):
        if self.user is None:
            (self.user, self.password) = urllib.FancyURLopener.prompt_user_passwd(self, host, realm)
        return (self.user, self.password)
        



tcgaConfig = {
    'AgilentG4502A_07': {
        ':dataSubType': 'geneExp',
        ':probeMap': 'hugo',
        ':sampleMap': 'tcga',
        'dataType': 'genomicMatrix',
        'probeField': 'log2 lowess normalized (cy5/cy3) collapsed by gene symbol',
        'extract' : TCGAGeneticFileScan,
        'compile' : GeneticDataCompile
    },
    'AgilentG4502A_07_1': {
        ':dataSubType': 'geneExp',
        ':probeMap': 'hugo',
        ':sampleMap': 'tcga',
        'dataType': 'genomicMatrix',
        'probeField': 'log2 lowess normalized (cy5/cy3) collapsed by gene symbol',
        'extract' : TCGAGeneticFileScan,
        'compile' : GeneticDataCompile
    },
    'AgilentG4502A_07_2': {
        ':dataSubType': 'geneExp',
        ':probeMap': 'hugo',
        ':sampleMap': 'tcga',
        'dataType': 'genomicMatrix',
        'probeField': 'log2 lowess normalized (cy5/cy3) collapsed by gene symbol',
        'extract' : TCGAGeneticFileScan,
        'compile' : GeneticDataCompile
    },
    'AgilentG4502A_07_3': {
        ':dataSubType': 'geneExp',
        ':probeMap': 'hugo',
        ':sampleMap': 'tcga',
        'dataType': 'genomicMatrix',
        'probeField': 'log2 lowess normalized (cy5/cy3) collapsed by gene symbol',
        'extract' : TCGAGeneticFileScan,
        'compile' : GeneticDataCompile
    },
    'CGH-1x1M_G4447A': {
        ':dataSubType': 'cna',
        ':sampleMap': 'tcga',
        'dataType': 'genomicSegment',
        'probeField': 'seg.mean',
        'extract' : TCGAGeneticFileScan,
        'compile' : GeneticDataCompile
    },
    'Genome_Wide_SNP_6': {
        ':assembly': 'hg18',
        ':dataSubType': 'cna',
        ':sampleMap': 'tcga',
        'dataType': 'genomicSegment',
        'probeField': 'seg.mean',
        'extract' : TCGAGeneticFileScan,
        'compile' : GeneticDataCompile
    },
    'H-miRNA_8x15K': {
        ':dataSubType': 'miRNAExp',
        ':probeMap': 'agilentHumanMiRNA',
        ':sampleMap': 'tcga',
        'dataType': 'genomicMatrix',
        'probeField': 'unc_DWD_Batch_adjusted',
        'extract' : TCGAGeneticFileScan,
        'compile' : GeneticDataCompile
    },
    'H-miRNA_8x15Kv2': {
        ':dataSubType': 'miRNAExp',
        ':probeMap': 'agilentHumanMiRNA',
        ':sampleMap': 'tcga',
        'dataType': 'genomicMatrix',
        'probeField': 'unc_DWD_Batch_adjusted',
        'extract' : TCGAGeneticFileScan,
        'compile' : GeneticDataCompile
    },
    'HG-CGH-244A': {
        ':dataSubType': 'cna',
        ':sampleMap': 'tcga',
        'dataType': 'genomicSegment',
        'probeField': 'Segment_Mean',
        'extract' : TCGAGeneticFileScan,
        'compile' : GeneticDataCompile
    },
    'HG-CGH-415K_G4124A': {
        ':dataSubType': 'cna',
        ':sampleMap': 'tcga',
        'chromeField': 'Chromosome',
        'dataType': 'genomicSegment',
        'endField': 'End',
        'probeField': 'Segment_Mean',
        'startField': 'Start',
        'extract' : TCGAGeneticFileScan,
        'compile' : GeneticDataCompile
    },
    'HT_HG-U133A': {
        ':dataSubType': 'geneExp',
        ':probeMap': 'affyU133a',
        ':sampleMap': 'tcga',
        'dataType': 'genomicMatrix',
        'probeField': 'Signal',
        'extract' : TCGAGeneticFileScan,
        'compile' : GeneticDataCompile
    },
    'HuEx-1_0-st-v2': {
        ':dataSubType': 'miRNAExp',
        ':probeMap': 'hugo',
        ':sampleMap': 'tcga',
        'dataType': 'genomicMatrix',
        'probeField': 'Signal',
        'fileInclude' :  '^.*gene.txt$|^.*sdrf.txt$',
        'extract' : TCGAGeneticFileScan,
        'compile' : GeneticDataCompile
    },
    'Human1MDuo': {
        ':dataSubType': 'cna',
        ':sampleMap': 'tcga',
        'dataType': 'genomicSegment',
        'probeField': 'mean',
        'extract' : TCGAGeneticFileScan,
        'compile' : GeneticDataCompile
    },
    'HumanHap550': {
        ':dataSubType': 'cna',
        ':sampleMap': 'tcga',
        'dataType': 'genomicSegment',
        'probeField': 'mean',  
        'extract' : TCGAGeneticFileScan,
        'compile' : GeneticDataCompile
    },
    'HumanMethylation27': {
        ':dataSubType': 'DNAMethylation',
        ':probeMap': 'illuminaHumanMethylation27',
        ':sampleMap': 'tcga',
        'dataType': 'genomicMatrix',
        'fileExclude' : '.*.adf.txt',
        'probeField': 'Beta_Value',
        'extract' : TCGAGeneticFileScan,
        'compile' : GeneticDataCompile
    },
    'HumanMethylation450': {
        ':dataSubType': 'DNAMethylation',
        ':probeMap': 'illuminaHumanMethylation450',
        ':sampleMap': 'tcga',
        'dataType': 'genomicMatrix',
        'fileExclude' : '.*.adf.txt',
        'probeField': 'Beta_value',
        'extract' : TCGAGeneticFileScan,
        'compile' : GeneticDataCompile
    },
    'IlluminaHiSeq_RNASeq': {
        ':sampleMap': 'tcga',
        ':dataSubType': 'geneExp',
        'fileInclude': '^.*annotated.gene.quantification.txt$|^.*sdrf.txt$',
        'probeField': 'RPKM',
        ':probeMap': 'hugo',
        'extract' : TCGAGeneticFileScan,
        'compile' : GeneticDataCompile
    },
    'bio' : {
        'fileInclude': '.*.xml$',
        'extract' : TCGAClinialScan,
        'compile' : ClinicalDataCompile
    }
}

def fileDigest( file ):
    md5 = hashlib.md5()
    with open(file,'rb') as f: 
        for chunk in iter(lambda: f.read(8192), ''): 
            md5.update(chunk)
    return md5.hexdigest()


def platform_list():
    q = CustomQuery("Platform")
    for e in q:
        yield e['name']

def supported_list():
    q = CustomQuery("Platform")
    for e in q:
        if e['name'] in tcgaConfig:
            yield e['name']

def platform_archives(platform):
    q = CustomQuery("Archive[Platform[@name=%s]][@isLatest=1]" % platform)
    out = {}
    for e in q:
        name = e['baseName']
        if name not in out:
            yield name
            out[name] = True


if __name__ == "__main__":
    
    parser = OptionParser()
    #Stack.addJobTreeOptions(parser) 
    
    parser.add_option("-a", "--platform-list", dest="platform_list", action="store_true", help="Get list of platforms", default=False)
    parser.add_option("-p", "--platform", dest="platform", help="Platform Selection", default=None)
    parser.add_option("-l", "--supported", dest="supported_list", action="store_true", help="List Supported Platforms", default=None)
    parser.add_option("-f", "--filelist", dest="filelist", help="List files needed to convert TCGA project basename into cgData", default=None)
    parser.add_option("-b", "--basename", dest="basename", help="Convert TCGA project basename into cgData", default=None)
    parser.add_option("-m", "--mirror", dest="mirror", help="Mirror Location", default=None)
    parser.add_option("-w", "--workdir", dest="workdir_base", help="Working directory", default="/tmp")
    parser.add_option("-o", "--out-dir", dest="outdir", help="Working directory", default="./")
    parser.add_option("-c", "--cancer", dest="cancer", help="List Archives by cancer type", default=None)
    parser.add_option("-d", "--download", dest="download", help="Download files for archive", default=None)
    parser.add_option("-e", "--level", dest="level", help="Data Level ", default="3")
    parser.add_option("-s", "--check-sum", dest="checksum", help="Check project md5", default=None)
    parser.add_option("-r", "--sanitize", dest="sanitize", action="store_true", help="Remove race/ethnicity from clinical data", default=False) 
      
    
    options, args = parser.parse_args()
    
    if options.platform_list:
        for e in platform_list():
            print e
    
    if options.supported_list:
        for e in supported_list():
            print e
            
    if options.platform:
        for name in platform_archives( options.platform ):
            print name

    if options.cancer is not None:
        q = CustomQuery("Archive[@isLatest=1][Disease[@abbreviation=%s]]" % (options.cancer))
        out = {}
        for e in q:
            name = e['baseName']
            if name not in out:
                print name
                out[name] = True

    if options.filelist:
        q = CustomQuery("Archive[@baseName=%s][@isLatest=1][ArchiveType[@type=Level_%s]]" % (options.filelist, options.level))
        for e in q:
            print e['deployLocation']
        q = CustomQuery("Archive[@baseName=%s][@isLatest=1][ArchiveType[@type=mage-tab]]" % (options.filelist))
        for e in q:
            print e['deployLocation']

    if options.checksum:
        urls = []
        q = CustomQuery("Archive[@baseName=%s][@isLatest=1][ArchiveType[@type=Level_%s]]" % (options.checksum, options.level))
        for e in q:
            urls.append( e['deployLocation'] )
        q = CustomQuery("Archive[@baseName=%s][@isLatest=1][ArchiveType[@type=mage-tab]]" % (options.checksum))
        for e in q:
            urls.append( e['deployLocation'] )
        
        for url in urls:
            dst = os.path.join(options.mirror, re.sub("^/", "", url))
            if not os.path.exists( dst ):
                print "NOT_FOUND:", dst
                continue
            if not os.path.exists( dst + ".md5" ):
                print "MD5_NOT_FOUND", dst
                continue

            handle = open( dst + ".md5" )
            line = handle.readline()
            omd5 = line.split(' ')[0]
            handle.close()

            nmd5 = fileDigest( dst )
            if omd5 != nmd5:
                print "CORRUPT:", dst
            else:
                print "OK:", dst


    if options.download is not None:
        if options.mirror is None:
            print "Define mirror location"
            sys.exit(1)
        q = CustomQuery("Archive[@baseName=%s][@isLatest=1][ArchiveType[@type=Level_%s]]" % (options.download, options.level))
        urls = []
        for e in q:
            urls.append( e['deployLocation'] )
            urls.append( e['deployLocation'] + ".md5" )
            
        q = CustomQuery("Archive[@baseName=%s][@isLatest=1][ArchiveType[@type=mage-tab]]" % (options.download))
        for e in q:
            urls.append( e['deployLocation'] )
            urls.append( e['deployLocation'] + ".md5" )

        u =  MyDownloader()
        for url in urls:
            src = "https://tcga-data.nci.nih.gov/" + url
            dst = os.path.join(options.mirror, re.sub("^/", "", url))
            dir = os.path.dirname(dst)
            if not os.path.exists(dir):
                print "mkdir", dir
                os.makedirs(dir)
            if not os.path.exists( dst ):
                print "download %s to %s" % (src, dst)
                u.retrieve(src, dst)

    if options.basename:
        if options.mirror is None:
            print "Need mirror location"
            sys.exit(1)

        ext = TCGAExtract(options)
        ext.run()
