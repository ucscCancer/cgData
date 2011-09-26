
import CGData
import binascii
import struct
from CGData.SQLUtil import *

CREATE_BED = """
CREATE TABLE %s (
    bin smallint unsigned not null,
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
    INDEX(chrom(5),bin)
) engine 'MyISAM';
"""


class TrackGenomic(CGData.CGMergeObject,CGData.CGSQLObject):

    typeSet = { 
        'clinicalMatrix' : True, 
        'genomicMatrix' : True,
        'sampleMap' : True,
        'probeMap' : True
    } 

    def __init__(self):
        CGData.CGMergeObject.__init__(self)
            
    def get_name( self ):
        return "%s" % ( self.members[ "genomicMatrix" ].get_name() )


    def gen_sql(self, id_table):
        CGData.CGMergeObject.gen_sql(self, id_table)

        gmatrix = self.members[ 'genomicMatrix' ]
        pmap = self.members[ 'probeMap' ].get( assembly="hg18" ) # BUG: hard coded to only producing HG18 tables
        if pmap is None:
            CGData.error("Missing HG18 %s" % ( self.members[ 'probeMap'].get_name() ))
            return
        
        table_base = self.get_name()
        CGData.log("Writing Track %s" % (table_base))
        
        clinical_table_base =  self.members[ "clinicalMatrix" ].get_name()

        yield "INSERT into raDb( name, sampleTable, clinicalTable, columnTable, aliasTable, shortLabel, longLabel, expCount, dataType, platform, profile, security) VALUES ( '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%d', '%s', '%s', '%s', '%s');\n" % \
            ( "genomic_" + table_base, "sample_" + table_base,
                "clinical_" + clinical_table_base, "clinical_" + clinical_table_base + "_colDb",
                "genomic_" + table_base + "_alias",
                sql_fix(gmatrix.attrs['shortTitle']),
                sql_fix(gmatrix.attrs['longTitle']),
                len(gmatrix.get_sample_list()),
                'bed 15b',
                gmatrix.attrs[':dataSubType'],
                'localDb',
                'public',
                )
        
        # write out the sample table
        yield "drop table if exists sample_%s;" % ( table_base )
        yield """
CREATE TABLE sample_%s (
    id           int,
    sampleName   varchar(255)
) engine 'MyISAM';
""" % ( table_base )

        for sample in gmatrix.get_sample_list():
            yield "INSERT INTO sample_%s VALUES( %d, '%s' );\n" % ( table_base, id_table.get( 'sample_id', sample), sample )

        
        yield "drop table if exists genomic_%s_alias;" % ( table_base )
        yield """
CREATE TABLE genomic_%s_alias (
    name        varchar(255),
    alias         varchar(255)
) engine 'MyISAM';
""" % ( table_base )

        for probe in pmap:
            for alias in probe.aliases:
                yield "insert into genomic_%s_alias( name, alias ) values( '%s', '%s' );\n" % (table_base, sql_fix(probe.name), sql_fix(alias))

        # write out the BED table
        yield "drop table if exists %s;" % ( "genomic_" + table_base )
        yield CREATE_BED % ( "genomic_" + table_base + "_tmp")
        
        sample_ids = []
        for sample in gmatrix.get_sample_list():
            sample_ids.append( str( id_table.get( 'sample_id', sample ) ) )
        
        missingProbeCount = 0
        for probe_name in gmatrix.get_probe_list():
            exp_ids = ','.join( sample_ids )
            row = gmatrix.get_row_vals( probe_name )
            exps = ''.join( binascii.hexlify(struct.pack('f', a)) for a in row )
#            exps = ','.join( str(a) for a in row )
            probe = pmap.get( probe_name )
            if probe is not None:
                #istr = "insert into %s(chrom, chromStart, chromEnd, strand,  name, expCount, expIds, expScores) values ( '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s' );\n" % \
                istr = "insert into %s(chrom, chromStart, chromEnd, strand,  name, expCount, expIds, expScores) values ( '%s', '%s', '%s', '%s', '%s', '%s', '%s', x'%s' );\n" % \
                    ( "genomic_%s_tmp" % (table_base), probe.chrom, probe.chrom_start, probe.chrom_end, probe.strand, sql_fix(probe_name), len(sample_ids), exp_ids, exps )
                yield istr
            else:
                missingProbeCount += 1
        yield "create table genomic_%s like genomic_%s_tmp;" % (table_base, table_base)
        yield "insert into genomic_%s select * from genomic_%s_tmp order by chrom, chromStart;" % (table_base, table_base)
        yield "drop table genomic_%s_tmp;" % table_base
        CGData.log("%s Missing probes %d" % (table_base, missingProbeCount))

    def unload(self):
        for t in self.members:
            self.members[t].unload()
