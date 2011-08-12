
import CGData
from CGData.SQLUtil import *

CREATE_BED = """
CREATE TABLE %s (
    bin smallint unsigned not null,
    chrom varchar(255) not null,
    chrom_start int unsigned not null,
    chrom_end int unsigned not null,
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
    INDEX(chrom(4),chrom_start),
    INDEX(chrom(4),bin)
);
"""


class Track(CGData.CGMergeObject,CGData.CGSQLObject):

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


    def build_ids(self, id_table):
        
        for sample in self.members[ 'genomicMatrix' ].get_sample_list():
            id_table.alloc( 'sampleID', sample)

    def gen_sql(self, id_table):

        gmatrix = self.members[ 'genomicMatrix' ]
        pmap = self.members[ 'probeMap' ].get( assembly="hg18" ) # BUG: hard coded to only producing HG18 tables
        if pmap is None:
            print "Missing HG18 %s" % ( self.members[ 'probeMap'].get_name() )
            return
        
        table_base = self.get_name()
        
        # write out the sample table
        yield "drop table if exists sample_%s;" % ( table_base )
        yield """
CREATE TABLE sample_%s (
    id           int,
    sampleName   varchar(255)
);
""" % ( table_base )

        for sample in gmatrix.get_sample_list():
            yield "INSERT INTO sample_%s VALUES( %d, '%s' );\n" % ( table_base, id_table.get( 'sampleID', sample), sample )

        # write out the BED table
        yield "drop table if exists %s;" % ( "genomic_" + table_base )
        yield CREATE_BED % ( "genomic_" + table_base )
        
        sample_ids = []
        for sample in gmatrix.get_sample_list():
            sample_ids.append( str( id_table.get( 'sampleID', sample ) ) )
        
        for probe_name in gmatrix.get_probe_list():
            exp_ids = ','.join( sample_ids )
            row = gmatrix.get_row_vals( probe_name )
            exps = ','.join( str(a) for a in row[1:])
            probe = pmap.get( probe_name )
            if probe is not None:
                istr = "insert into %s(chrom, chromStart, chromEnd, strand,  name, expCount, expIds, expScores) values ( '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s' );\n" % \
                    ( "genomic_%s" % (table_base), probe.chrom, probe.chrom_start, probe.chrom_end, probe.strand, sql_fix(probe_name), len(exps), exp_ids, exps )
                yield istr
            else:
                print "Probe not found:", probe_name
        

        #raDbHandle.write( "INSERT into raDb( name, sampleTable, clinicalTable, columnTable, aliasTable, shortLabel) VALUES ( '%s', '%s', '%s', '%s', '%s', '%s');\n" % \
        #    ( "genomic_" + genomicName, "sample_" + sampleName, "clinical_" + clinicalNames[0], "clinical_" + clinicalNames[0] + "_colDb", "genomic_" + genomicName + "_alias", genomicName ))
		
