
import CGData
import binascii
import datetime,string
import struct
from CGData.SQLUtil import *
import json
from RangeFinder import Binner

CREATE_BED = """
CREATE TABLE %s (
    id int unsigned not null primary key auto_increment,
    bin int(11) NOT NULL,
    chrom varchar(255) not null,
    chromStart int unsigned not null,
    chromEnd int unsigned not null,
    name varchar(255) not null,
    score int not null,
    strand char(1) not null,
    thickStart int unsigned not null,
    thickEnd int unsigned not null,
    reserved int unsigned  not null,
    blockCount int unsigned not null,
    blockSizes longblob not null,
    chromStarts longblob not null,
    expCount int unsigned not null,
    expIds longblob not null,
    expScores longblob not null,
    INDEX(name(16)),
    INDEX(chrom(7),bin)
) engine 'MyISAM';
"""

dataSubTypeMap = {
    'cna': 'CNV',
    'geneExp': 'expression',
    }

def makeDate(isoFormatDate):
    data = string.split(isoFormatDate,"-")
    if len(data)!=3:
        return None
    for i in range (0,len(data)):
        try:
            int(data[i])
        except TypeError:
            return None
    y,m,d = data
    DATE = datetime.date(int(y), int(m), int(d))
    return DATE

class TrackGenomic(CGData.CGMergeObject):

    DATA_FORM = None

    typeSet = {
        'clinicalMatrix' : True,
        'genomicMatrix' : True,
        'sampleMap' : True,
        'probeMap' : True
    }

    format = "bed 15"

    def __init__(self):
        CGData.CGMergeObject.__init__(self)
            
    def get_name( self ):
        return "%s" % ( self.members[ "genomicMatrix" ].get_name() )

    def scores(self, row):
        return "'%s'" % (','.join( str(a) for a in row ))

    def gen_sql_heatmap(self, id_table, opts):
        #scan the children
        # XXX Handling of sql for children is broken if the child may appear
        # as part of multiple merge objects, such as TrackGenomic and TrackClinical.
        # A disgusting workaround for clinicalMatrix is to prevent the TrackGenomic from calling
        # it for gen_sql.
        clinical = self.members.pop("clinicalMatrix")
        for line in CGData.CGMergeObject.sql_pass(self, id_table, method="heatmap"):
            yield line
        self.members["clinicalMatrix"] = clinical

        gmatrix = self.members[ 'genomicMatrix' ]
        pmap = self.members[ 'probeMap' ].lookup( assembly="hg18" ) # BUG: hard coded to only producing HG18 tables
        if pmap is None:
            CGData.error("Missing HG18 %s" % ( self.members[ 'probeMap'].get_name() ))
            return

        savedownsample = 'save-ds' in opts and opts['save-ds']
        
        table_base = self.get_name().replace(".", "_")
        CGData.log("Writing Track %s" % (table_base))
        
        clinical_table_base =  self.members[ "clinicalMatrix" ].get_name().replace(".", "_")

        other = {}
        for attr in ['wrangler', 'wrangling_procedure', 'url', 'citation', 'description']:
            if attr in gmatrix:
                other[attr] = gmatrix[attr]
        if 'dataProducer' in gmatrix:
            other['author_list'] = gmatrix['dataProducer']
        if 'articleTitle' in gmatrix:
            other['article_title'] = gmatrix['articleTitle']

        ##TO DO, the version info should be the lastest of genomic and clinical, currently only check genomic
        cVersion= self.members[ 'clinicalMatrix' ].get('version',"")
        gVersion= self.members[ 'genomicMatrix' ].get('version',"")
        dG= makeDate(gVersion)
        dC= makeDate(cVersion)
        if dC == None:
            other['version'] = gVersion
        elif dG<dC:
            other['version'] = cVersion
        else:
            other['version'] = gVersion
        datetime.datetime.strptime(other['version'], "%Y-%m-%d") #if the version isn't properly formatted, though exception

        if 'owner' in gmatrix:
            other['owner'] = gmatrix['owner']
        other['colNormalization'] = gmatrix.get('colNormalization', False)
        if not isinstance(other['colNormalization'], bool):
            other['colNormalization']  = False
        other['redistribution'] = gmatrix.get('redistribution', False)
        if not isinstance(other['redistribution'], bool):
            other['redistribution']  = False
        security = gmatrix.get('security', "public")
        if security not in [ "public", "private" ]:
            security = "public"

        if savedownsample:
            yield "SET @ds=(SELECT downSampleTable FROM raDb WHERE name = '%s');\n" % ("genomic_" + table_base)
        yield "DELETE from raDb where name = '%s';\n" % ("genomic_" + table_base)
        yield "INSERT into raDb( name, downSampleTable, sampleTable, clinicalTable, columnTable, aliasTable, shortLabel, longLabel, expCount, dataType, platform, profile, security, priority, gain, groupName, wrangler, url, article_title, citation, author_list, wrangling_procedure, other) VALUES ( '%s', %s, '%s', '%s', '%s', '%s', '%s', '%s', '%d', '%s', '%s', '%s', '%s', %f, %f, '%s', %s, %s, %s, %s, %s, %s, '%s');\n" % \
            ( "genomic_" + table_base,
                "@ds" if savedownsample else "NULL",
                "sample_" + table_base,
                "clinical_" + clinical_table_base, "colDb",
                "genomic_" + table_base + "_alias",
                sql_fix(gmatrix['shortTitle']),
                sql_fix(gmatrix['longTitle']),
                len(gmatrix.get_sample_list()),
                self.format,
                dataSubTypeMap[gmatrix[':dataSubType']] if gmatrix[':dataSubType'] in dataSubTypeMap else gmatrix[':dataSubType'],
                'localDb',
                security,
                float(gmatrix.get('priority', 1.0)),
                float(gmatrix.get('gain', 1.0)),
                sql_fix(gmatrix.get('groupTitle', 'Misc.')),
                "'%s'"%sql_fix(gmatrix['wrangler']) if 'wrangler' in gmatrix else '\N',
                "'%s'"%sql_fix(gmatrix['url']) if 'url' in gmatrix else '\N',
                "'%s'"%sql_fix(gmatrix['articleTitle']) if 'articleTitle' in gmatrix else '\N',
                "'%s'"%sql_fix(gmatrix['citation']) if 'citation' in gmatrix else '\N',
                "'%s'"%sql_fix(gmatrix['dataProducer']) if 'dataProducer' in gmatrix else '\N',
                "'%s'"%sql_fix(gmatrix['wrangling_procedure']) if 'wrangling_procedure' in gmatrix else '\N',
                sql_fix(json.dumps(other)),
                )

        if 'no-genomic-matrix' in opts and opts['no-genomic-matrix']:
            return
        
        # write out the sample table
        yield "drop table if exists sample_%s;" % ( table_base )
        yield """
        CREATE TABLE sample_%s (
        id           int,
        sampleName   varchar(255)
        ) engine 'MyISAM';
        """ % ( table_base )

        from CGData.ClinicalMatrix import sortedSamples
        for sample in sortedSamples(gmatrix.get_sample_list()):
            yield "INSERT INTO sample_%s VALUES( %d, '%s' );\n" % ( table_base, id_table.get( clinical_table_base + ':sample_id', sample), sql_fix(sample) )

        
        yield "drop table if exists genomic_%s_alias;" % ( table_base )
        yield """
        CREATE TABLE genomic_%s_alias (
        name        varchar(255),
        alias         varchar(255)
        ) engine 'MyISAM';
        """ % ( table_base )

        for probe in pmap.get_probes():
            for alias in probe.aliases:
                yield "insert into genomic_%s_alias( name, alias ) values( '%s', '%s' );\n" % (table_base, sql_fix(probe.name), sql_fix(alias))

        # write out the BED table
        yield "drop table if exists %s;" % ( "genomic_" + table_base )
        yield CREATE_BED % ( "genomic_" + table_base + "_tmp")
        
        sample_ids = []
        samples = gmatrix.get_sample_list()

        # sort samples by sample_id, and retain the sort order for application to the genomic data, below
        tmp=sorted(zip(samples, range(len(samples))), cmp=lambda x,y: id_table.get(clinical_table_base + ':sample_id', x[0]) - id_table.get( clinical_table_base + ':sample_id', y[0]))
        samples, order = map(lambda t: list(t), zip(*tmp))

        for sample in samples:
            sample_ids.append( str( id_table.get( clinical_table_base + ':sample_id', sample ) ) )
        
        exp_ids = ','.join( sample_ids )
        missingProbeCount = 0
        for probe_name in gmatrix.get_probe_list():
            # get the genomic data and rearrange to match the sample_id order
            tmp = gmatrix.get_row_vals( probe_name )
            row = map(lambda i: tmp[order[i]], range(len(tmp)))

            pset = pmap.lookup( probe_name )
            if pset is not None:
                for probe in pset:
                    istr = "insert into %s(bin, chrom, chromStart, chromEnd, strand,  name, expCount, expIds, expScores) values ( %d, '%s', '%s', '%s', '%s', '%s', '%s', '%s', %s );\n" % \
                            ( "genomic_%s_tmp" % (table_base), Binner.calcBin(probe.chrom_start, probe.chrom_end), probe.chrom, probe.chrom_start-1, probe.chrom_end, probe.strand, sql_fix(probe_name), len(sample_ids), exp_ids, self.scores(row) )
                    yield istr
            else:
                missingProbeCount += 1
        yield "# sort file by chrom position\n"
        yield "create table genomic_%s like genomic_%s_tmp;\n" % (table_base, table_base)
        yield "insert into genomic_%s(bin, chrom, chromStart, chromEnd, strand,  name, expCount, expIds, expScores) select bin, chrom, chromStart, chromEnd, strand,  name, expCount, expIds, expScores from genomic_%s_tmp order by chrom, chromStart;\n" % (table_base, table_base)
        yield "drop table genomic_%s_tmp;\n" % table_base
        CGData.log("%s Missing probes %d" % (table_base, missingProbeCount))

    def unload(self):
        for t in self.members:
            self.members[t].unload()

class BinaryTrackGenomic(TrackGenomic):
    format = 'bed 15b'
    def scores(self, row):
        return  "x'%s'" % (''.join( binascii.hexlify(struct.pack('f', a)) for a in row ))
