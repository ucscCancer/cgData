
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

    format = "bed 15"

    def __init__(self):
        CGData.CGMergeObject.__init__(self)
            
    def get_name( self ):
        return "%s" % ( self.members[ "genomicMatrix" ].get_name() )

    def scores(self, row):
        return "'%s'" % (','.join( str(a) for a in row ))

    def gen_sql(self, id_table):
        #scan the children
        for line in CGData.CGMergeObject.gen_sql(self, id_table):
            yield line

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
                self.format,
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

        for pset in pmap:
            for probe in pset:
                for alias in probe.aliases:
                    yield "insert into genomic_%s_alias( name, alias ) values( '%s', '%s' );\n" % (table_base, sql_fix(probe.name), sql_fix(alias))

        # write out the BED table
        yield "drop table if exists %s;" % ( "genomic_" + table_base )
        yield CREATE_BED % ( "genomic_" + table_base + "_tmp")
        
        sample_ids = []
        samples = gmatrix.get_sample_list()

        # sort samples by sample_id, and retain the sort order for application to the genomic data, below
        tmp=sorted(zip(samples, range(len(samples))), cmp=lambda x,y: id_table.get('sample_id', x[0]) - id_table.get( 'sample_id', y[0]))
        samples, order = map(lambda t: list(t), zip(*tmp))

        for sample in samples:
            sample_ids.append( str( id_table.get( 'sample_id', sample ) ) )
        
        exp_ids = ','.join( sample_ids )
        missingProbeCount = 0
        for probe_name in gmatrix.get_probe_list():
            # get the genomic data and rearrange to match the sample_id order
            tmp = gmatrix.get_row_vals( probe_name )
            row = map(lambda i: tmp[order[i]], range(len(tmp)))

            pset = pmap.get( probe_name )
            if pset is not None:
                for probe in pset:
                    istr = "insert into %s(chrom, chromStart, chromEnd, strand,  name, expCount, expIds, expScores) values ( '%s', '%s', '%s', '%s', '%s', '%s', '%s', %s );\n" % \
                            ( "genomic_%s_tmp" % (table_base), probe.chrom, probe.chrom_start, probe.chrom_end, probe.strand, sql_fix(probe_name), len(sample_ids), exp_ids, self.scores(row) )
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

class BinaryTrackGenomic(TrackGenomic):
    format = 'bed 15b'
    def scores(self, row):
        return  "x'%s'" % (''.join( binascii.hexlify(struct.pack('f', a)) for a in row ))
