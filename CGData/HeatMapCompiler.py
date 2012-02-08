
import sys
import os
import csv
from glob import glob
import json
from copy import copy
import CGData
import CGData.CGZ
import CGData.FeatureDescription


from CGData import info, error, warn
import re

CREATE_COL_DB = """
CREATE TABLE `%s` (
  `id` int(10) unsigned NOT NULL PRIMARY KEY AUTO_INCREMENT,
  `name` varchar(255) NOT NULL UNIQUE,
  `shortLabel` varchar(255) default NULL,
  `longLabel` varchar(255) default NULL,
  `valField` varchar(255) default NULL,
  `clinicalTable` varchar(255) default NULL,
  `priority` float default NULL,
  `filterType` varchar(255) default NULL,
  `visibility` varchar(255) default NULL,
  `groupName` varchar(255) default NULL
) engine 'MyISAM';
"""

    
CREATE_BED = """
CREATE TABLE %s (
    id int unsigned not null primary key auto_increment,
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
    INDEX(chrom(5),id)
) engine 'MyISAM';
"""

NULL_VALUES = ['NULL', 'NONE', 'NA', '']


dataSubTypeMap = {
    'cna': 'CNV',
    'geneExp': 'expression',
    'SNP': 'SNP',
    'RPPA': 'RPPA',
    'DNAMethylation' : 'DNAMethylation',
    'PARADIGM.pathlette' : 'PARADIGM.pathlette'
    }


def col_fix( name ):
    out = name.replace('`', '_').replace('\\','_').strip()
    while (len(out) > 64):
        out = re.sub( r'[aeiou]([^aioeu]*)$', r'\1', out)
    return out

def sql_fix( name ):
    return name.replace("\\", "\\\\").replace("'", "\\'")

def tableName_fix(name):
    return name.replace(".", "_").replace("-", "_")

class CGIDTable(object):
    
    def __init__(self):
        self.id_table = {}
    
    def get( self, itype, iname ):
        if itype not in self.id_table:
            self.id_table[ itype ] = {}
        if iname not in self.id_table[ itype ]:
            self.id_table[ itype ][ iname ] = len( self.id_table[ itype ] )
            
        return self.id_table[ itype ][ iname ]


class BrowserCompiler(object):
    
    PARAMS = [ "compiler.mode" ]

    def __init__(self,data_set,params={}):
        #import CGData.ClinicalFeature
        self.out_dir = "out"
        self.params = params
        self.set_hash = data_set

        # Create a default null clinicalFeature, to coerce creation of a TrackClinical merge object.
        #if not 'clinicalFeature' in self.set_hash:
        #    self.set_hash['clinicalFeature'] = {}
        #self.set_hash['clinicalFeature']['__null__'] = CGData.ClinicalFeature.NullClinicalFeature()

        #if 'binary' in self.params and self.params['binary']:
        #    CGData.OBJECT_MAP['trackGenomic'] = ('CGData.TrackGenomic', 'BinaryTrackGenomic')

    
    def gen_sql(self):
        """
        Scan found object records and determine if the data they link to is
        avalible
        """    
        
        self.id_table = CGIDTable()
        if not os.path.exists(self.out_dir):
            os.makedirs(self.out_dir)

        
        for gmatrix_name in self.set_hash[ 'genomicMatrix' ]:
            info("GenomicMatrix: " + gmatrix_name) 
            gmatrix = self.set_hash['genomicMatrix'][gmatrix_name]
            
            #query to fine all id spaces that link to current genomic matrix
            idList = self.set_hash.query(src_type="genomicMatrix", src_name=gmatrix_name, predicate="columnKeySrc", dst_type='idDAG')
            if len(idList) == 0:
                error("IDDag not found")
                continue
            idName = idList[0].dst_name
            info( "Using idDag: " + idName)
            if 'idDAG' not in self.set_hash or idName not in self.set_hash['idDAG']:
                error("idDAG for %s not found\n" % (idName))
                continue
                
            idmap = {}
            for row in self.set_hash.query( dst_type='idDAG', dst_name=idName ):
                if row.src_type not in idmap:
                    idmap[row.src_type] = []
                idmap[row.src_type].append( row.src_name )
            
            if 'clinicalMatrix' not in idmap:
                error("Clinical Matrix for %s not found" % (gmatrix_name))
                continue
            
            tg = TrackGenomic()
            tg.merge( 
                genomicMatrix=gmatrix, 
                idDAG=self.set_hash['idDAG'][idName], 
                clinicalMatrix=self.set_hash['clinicalMatrix'][idmap['clinicalMatrix'][0]]
            )
            
            #query to find the probe key space that matches the current probemap
            probeList = self.set_hash.query( src_type="genomicMatrix", src_name=gmatrix_name, dst_type="probe" )
            probeName = probeList[0].dst_name
            
            #find probeMap that connects to probe
            probeMapList = self.set_hash.query( dst_type="probe", dst_name=probeName, src_type="probeMap" )
            if len(probeMapList) == 0:
                error("ProbeMap not found: " + probeName )
                continue
            probeMapName = probeMapList[0].src_name
            #find aliasMap that connects to probe
            aliasMapList = self.set_hash.query( dst_type="probe", dst_name=probeName, src_type="aliasMap" )
            aliasMapName = aliasMapList[0].src_name
            
            
            tg.merge(
                probeMap = self.set_hash['probeMap'][probeMapName],
                aliasMap = self.set_hash['aliasMap'][aliasMapName]                
            )
            
            shandle = tg.gen_sql(self.id_table)
            if shandle is not None:
                ohandle = open( os.path.join( self.out_dir, "%s.%s.sql" % (tg.get_type(), tg.get_name() ) ), "w" )
                for line in shandle:
                    ohandle.write( line )
                ohandle.close()
                
        
        for cmatrix_name in self.set_hash[ 'clinicalMatrix' ]:
            cmatrix = self.set_hash['clinicalMatrix'][cmatrix_name]
            tc = TrackClinical()
            tc.merge( clinicalMatrix=cmatrix )
            
            if 'columnKeySrc' in cmatrix.get_link_map():
                featureDescList = self.set_hash.query( 
                    dst_type="clinicalFeature", 
                    dst_name=cmatrix.get_link_map()['columnKeySrc']['name']
                )
                featureDescName = featureDescList[0].dst_name
                if 'featureDescription' not in self.set_hash or featureDescName not in self.set_hash['featureDescription']:
                    error("Clinical Feature Desc %s not found" % (featureDescName))
                    continue                
                tc.merge( featureDescription=self.set_hash['featureDescription'][featureDescName] )
            else:
                tc.merge( featureDescription=CGData.FeatureDescription.NullClinicalFeature() )
            shandle = tc.gen_sql(self.id_table)
            if shandle is not None:
                ohandle = open( os.path.join( self.out_dir, "%s.%s.sql" % (tc.get_type(), tc.get_name() ) ), "w" )
                for line in shandle:
                    ohandle.write( line )
                ohandle.close()
    
    def __iter__(self):
        return self.compile_matrix.__iter__()
        
    def __getitem__(self, item):
        return self.compile_matrix[item]





def sortedSamples(samples):
    import os, re
    # Check for numeric sample ids. Allow for a common prefix
    # before the number.
    prefix = os.path.commonprefix(samples)
    plen = len(prefix)
    if reduce(lambda x,y: x and y, map(lambda s: re.match('^' + prefix + '[0-9]+$', s), samples)):
        return sorted(samples, cmp=lambda x, y: int(x[plen:]) - int(y[plen:]))
    else:
        return sorted(samples)

        
class TrackClinical:
    type_name = "trackClinical"
    DATA_FORM = None

    typeSet = { 
        'clinicalMatrix' : True, 
        'featureDescription' : True
    } 

    def __init__(self):
        self.members = {}

    def merge(self, **kw):
        for k in kw:
            if k in self.typeSet:
                self.members[k] = kw[k]
    
    def get_name( self ):
        return "%s" % ( self.members[ "clinicalMatrix" ].get_name() )

    def get_type( self ):
        return 'trackClinical'

    def gen_sql(self, id_table):
        CGData.info("ClincalTrack SQL " + self.get_name())

        features = {}
        fmap = self.members["featureDescription"].get_feature_map()
        for feat in fmap:
            features[feat] = {}
            for ent in fmap[feat]:
                features[feat][ent] = []
                for val in fmap[feat][ent]:
                    features[feat][ent].append( val.value )

        matrix = self.members["clinicalMatrix"]
        # e.g. { 'HER2+': 'category', ...}
        explicit_types = dict((f, features[f]['valueType'][0]) for f in features if 'valueType' in features[f])
        self.feature_type_setup(explicit_types)
        for a in features:
            if "stateOrder" in features[a]:
                read = csv.reader( [features[a]["stateOrder"][0]], skipinitialspace=True)
                enums = read.next()
                i = 0
                for e in self.enum_map[a]:
                    if e in enums:
                        self.enum_map[a][e] = enums.index(e)
                    else:
                        self.enum_map[a][e] = len(enums) + i
                        i += 1
        for a in self.gen_sql_clinicalMatrix(id_table, features=features):
            yield a


    def gen_sql_clinicalMatrix(self, id_table, features=None):
        matrix = self.members["clinicalMatrix"]
        CGData.info( "Writing Clinical %s SQL" % (matrix.get_name()))
        
        features['sampleName'] = { 'shortTitle': ['Sample name'], 'longTitle': ['Sample name'], 'visibility': ['on'], 'priority': [1] }

        table_name = tableName_fix(matrix.get_name())
        clinical_table = 'clinical_' + table_name
        yield "DROP TABLE IF EXISTS %s;\n" % ( clinical_table )
        yield "DELETE codes FROM codes, colDb WHERE codes.feature = colDb.id AND colDb.clinicalTable = '%s';\n" % clinical_table
        yield "DELETE FROM colDb WHERE clinicalTable = '%s';\n" % clinical_table

        
        # colDb
        i = 0;
        for name in self.col_order:
            shortLabel = name if name not in features or 'shortTitle' not in features[name] else features[name]['shortTitle'][0]
            longLabel = name if name not in features or 'longTitle' not in features[name] else features[name]['longTitle'][0]
            filter = 'coded' if self.enum_map.has_key(name) else 'minMax'
            visibility = ('on' if i < 10 else 'off') if name not in features or 'visibility' not in features[name] else features[name]['visibility'][0]
            priority = 1 if name not in features or 'priority' not in features[name] else float(features[name]['priority'][0])
            yield "INSERT INTO colDb(name, shortLabel,longLabel,valField,clinicalTable,filterType,visibility,priority) VALUES( '%s', '%s', '%s', '%s', '%s', '%s', '%s', %f);" % \
                    ( sql_fix(name), sql_fix(shortLabel), sql_fix(longLabel), sql_fix(name), clinical_table, filter, visibility, priority)
            yield "SET @col%d=LAST_INSERT_ID();\n" % i
            i += 1

        # codes
        i = 0;
        values = {}
        for col in self.col_order:
            if ( self.enum_map.has_key( col ) ):
                values[col] = {}
                j = 0
                for a in sorted(self.enum_map[ col ].keys(), lambda x,y: self.enum_map[col][x]-self.enum_map[col][y]):
                    yield "INSERT INTO codes(feature,ordering,value) VALUES (@col%d, %d, '%s'); SET @val%d_%d=LAST_INSERT_ID();\n" % (i, j, sql_fix(a), i, j)
                    values[col][a] = "@val%d_%d" % (i, j)
                    j += 1
            i += 1


        yield "CREATE TABLE %s (sampleID INT NOT NULL UNIQUE" % clinical_table

        for col in self.col_order:
            if col == 'sampleName':
                yield ",\n\tsampleName INT UNSIGNED NOT NULL UNIQUE"
            else:
                if self.enum_map.has_key(col):
                    yield ",\n\t`%s` INT UNSIGNED DEFAULT NULL" % (col.strip())
                else:
                    yield ",\n\t`%s` FLOAT DEFAULT NULL" % (col.strip())
        yield """
    ) engine 'MyISAM';
    """

        for target in sortedSamples(matrix.get_row_list()):
            a = []
            for col,orig in zip(self.col_order, self.orig_order):
                if col == 'sampleName':
                    val = target
                else:
                    val = matrix.get_val( row_name=target, col_name=orig )
                if val is None or val.upper() in NULL_VALUES:
                    a.append("\\N")
                else:
                    if col in self.enum_map:
                        a.append(values[col][val])
                    else:
                        a.append(val)
            yield u"INSERT INTO %s VALUES ( %d, %s );\n" % ( clinical_table, id_table.get( table_name + ':sample_id', target ), u",".join(a) )



    def feature_type_setup(self, types = {}):
        
        cmatrix = self.members['clinicalMatrix']
        cmatrix.load()
        self.float_map = {}
        self.enum_map = {}
        self.enum_map['sampleName'] = dict((k,v) for k,v in zip(sortedSamples(cmatrix.get_row_list()), range(0,len(cmatrix.get_row_list()))))

        for key in cmatrix.get_col_list():
            # get unique list of values by converting to a set & back.
            # also, drop null values.
            values = list(set([v for v in cmatrix.get_col(key) if v not in ["null", "None", "NA"] and v is not None and len(v)]))
            if not key in types:
                types[key] = cmatrix.__guess_type__(values)
            if len(values) > 0: # drop empty columns. XXX is this correct behavior?
                if types[key] in ['float']:
                    self.float_map[key] = True
                else:
                    self.enum_map[key] = dict((enum, order) for enum, order in zip(sorted(values), range(len(values))))
        id_map = {}
        id_num = 0
        prior = 1
        self.col_order = []
        self.orig_order = []    

        for name in self.float_map:
            id_map[ name ] = id_num
            id_num += 1    
            colName = col_fix( name )
            self.col_order.append( colName )
            self.orig_order.append( name )
            
        for name in self.enum_map:        
            id_map[ name ] = id_num
            id_num += 1    
            colName = col_fix( name )
            self.col_order.append( colName )
            self.orig_order.append( name )
    
       


class TrackGenomic:
    type_name = "trackGenomic"

    DATA_FORM = None

    typeSet = {
        'clinicalMatrix' : True,
        'genomicMatrix' : True,
        'idDAG' : True,
        'probeMap' : True,
        'aliasMap' : True
    }

    format = "bed 15"

    def __init__(self):
        self.members = {}

    def merge(self, **kw):
        for k in kw:
            if k in self.typeSet:
                self.members[k] = kw[k]
        
            
    def get_name( self ):
        return "%s" % ( self.members[ "genomicMatrix" ].get_name() )
    
    def get_type( self ):
        return 'trackGenomic'

    def scores(self, row):
        return "'%s'" % (','.join( str(a) for a in row ))

    def gen_sql(self, id_table):
        #scan the children
        # XXX Handling of sql for children is broken if the child may appear
        # as part of multiple merge objects, such as TrackGenomic and TrackClinical.
        # A disgusting workaround for clinicalMatrix is to prevent the TrackGenomic from calling
        # it for gen_sql.
        clinical = self.members.pop("clinicalMatrix")
        
        self.members["clinicalMatrix"] = clinical

        gmatrix = self.members[ 'genomicMatrix' ]
        pmap = self.members[ 'probeMap' ] # BUG: hard coded to only producing HG18 tables
        if pmap is None:
            CGData.error("Missing HG18 %s" % ( self.members[ 'probeMap'].get_name() ))
            return
        iddag = self.members['idDAG']
        table_base = tableName_fix(self.get_name())
        CGData.info("Writing Track %s" % (table_base))
        
        clinical_table_base =  self.members[ "clinicalMatrix" ].get_name()
        
        shortTitle = gmatrix.get_name()
        longTitle = gmatrix.get_name()
        if 'shortTitle' in gmatrix:
            shortTitle = gmatrix['shortTitle']
        if 'longTitle' in gmatrix:
            shortTitle = gmatrix['longTitle']
            
        
        yield "DELETE from raDb where name = '%s';\n" % ("genomic_" + table_base)
        yield "INSERT into raDb( name, sampleTable, clinicalTable, columnTable, aliasTable, shortLabel, longLabel, expCount, dataType, platform, profile, security, priority, gain, groupName, wrangler, url, article_title, citation, author_list, wrangling_procedure) VALUES ( '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%d', '%s', '%s', '%s', '%s', %f, %f, '%s', %s, %s, %s, %s, %s, %s);\n" % \
            ( "genomic_" + table_base, "sample_" + table_base,
                "clinical_" + clinical_table_base, "colDb",
                "genomic_" + table_base + "_alias",
                sql_fix(shortTitle),
                sql_fix(longTitle),
                len(gmatrix.get_sample_list()),
                self.format,
                dataSubTypeMap[gmatrix.get_data_subtype()],
                'localDb',
                'public',
                float(gmatrix.get('priority', 1.0)),
                float(gmatrix.get('gain', 1.0)),
                sql_fix(gmatrix.get('groupTitle', 'Misc.')),
                "'%s'"%sql_fix(gmatrix['wrangler']) if 'wrangler' in gmatrix else '\N',
                "'%s'"%sql_fix(gmatrix['url']) if 'url' in gmatrix else '\N',
                "'%s'"%sql_fix(gmatrix['articleTitle']) if 'articleTitle' in gmatrix else '\N',
                "'%s'"%sql_fix(gmatrix['citation']) if 'citation' in gmatrix else '\N',
                "'%s'"%sql_fix(gmatrix['dataProducer']) if 'dataProducer' in gmatrix else '\N',
                "'%s'"%sql_fix(gmatrix['wrangling_procedure']) if 'wrangling_procedure' in gmatrix else '\N',
                )
        
        # write out the sample table
        yield "drop table if exists sample_%s;" % ( table_base )
        yield """
CREATE TABLE sample_%s (
    id           int,
    sampleName   varchar(255)
) engine 'MyISAM';
""" % ( table_base )

        for sample in sortedSamples(gmatrix.get_sample_list()):
            yield "INSERT INTO sample_%s VALUES( %d, '%s' );\n" % ( table_base, id_table.get( clinical_table_base + ':sample_id', sample), sql_fix(sample) )
            if not iddag.in_graph(sample):
                CGData.error("idDAG missing '%s'" % (sample))
        
        yield "drop table if exists genomic_%s_alias;" % ( table_base )
        yield """
CREATE TABLE genomic_%s_alias (
    name        varchar(255),
    alias         varchar(255)
) engine 'MyISAM';
""" % ( table_base )
        
        for aliasList in self.members['aliasMap'].get_probe_values():
            for alias in aliasList:
                yield "insert into genomic_%s_alias( name, alias ) values( '%s', '%s' );\n" % (table_base, sql_fix(alias.probe), sql_fix(alias.alias))

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
            tmp = gmatrix.get_row( probe_name )
            row = map(lambda i: tmp[order[i]], range(len(tmp)))
            #pset = pmap.get_by_probe( probe_name )
            probe = None
            try:
                probe = pmap.get_by_probe( probe_name )
            except KeyError:
                pass
            if probe is not None:
                #for probe in pset:
                    istr = "insert into %s(chrom, chromStart, chromEnd, strand,  name, expCount, expIds, expScores) values ( '%s', '%s', '%s', '%s', '%s', '%s', '%s', %s );\n" % \
                            ( "genomic_%s_tmp" % (table_base), probe.chrom, probe.chrom_start, probe.chrom_end, probe.strand, sql_fix(probe_name), len(sample_ids), exp_ids, self.scores(row) )
                    yield istr
            else:
                missingProbeCount += 1
        yield "# sort file by chrom position\n"
        yield "create table genomic_%s like genomic_%s_tmp;\n" % (table_base, table_base)
        yield "insert into genomic_%s select * from genomic_%s_tmp order by chrom, chromStart;\n" % (table_base, table_base)
        yield "drop table genomic_%s_tmp;\n" % table_base
        if missingProbeCount > 0:
            CGData.info("%s Missing probes %d" % (table_base, missingProbeCount))

    def unload(self):
        for t in self.members:
            self.members[t].unload()

    


class BinaryTrackGenomic(TrackGenomic):
    format = 'bed 15b'
    def scores(self, row):
        return  "x'%s'" % (''.join( binascii.hexlify(struct.pack('f', a)) for a in row ))
