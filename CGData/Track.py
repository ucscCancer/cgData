
import CGData
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
    INDEX(chrom(4),chromStart),
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


    def build_ids(self, idTable):
        
        for sample in self.members[ 'genomicMatrix' ].get_sample_list():
            idTable.alloc( 'sampleID', sample)

    def gen_sql(self, idTable):

        gMatrix = self.members[ 'genomicMatrix' ]
        pMap = self.members[ 'probeMap' ].get( assembly="hg18" ) # BUG: hard coded to only producing HG18 tables
        if pMap is None:
            print "Missing HG18 %s" % ( self.members[ 'probeMap'].get_name() )
            return
        
        tableBase = self.get_name()
        
        # write out the sample table
        yield "drop table if exists sample_%s;" % ( tableBase )
        yield """
CREATE TABLE sample_%s (
    id           int,
    sampleName   varchar(255)
);
""" % ( tableBase )

        for sample in gMatrix.get_sample_list():
            yield "INSERT INTO sample_%s VALUES( %d, '%s' );\n" % ( tableBase, idTable.get( 'sampleID', sample), sample )

        # write out the BED table
        yield "drop table if exists %s;" % ( "genomic_" + tableBase )
        yield CREATE_BED % ( "genomic_" + tableBase )
        
        sampleIDs = []
        for sample in gMatrix.get_sample_list():
            sampleIDs.append( str( idTable.get( 'sampleID', sample ) ) )
        
        for probeName in gMatrix.get_probe_list():
            expIDs = ','.join( sampleIDs )
            row = gMatrix.get_row_vals( probeName )
            exps = ','.join( str(a) for a in row[1:])
            probe = pMap.get( probeName )
            if probe is not None:
                iStr = "insert into %s(chrom, chromStart, chromEnd, strand,  name, expCount, expIds, expScores) values ( '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s' );\n" % \
                    ( "genomic_%s" % (tableBase), probe.chrom, probe.chromStart, probe.chromEnd, probe.strand, sql_fix(probeName), len(exps), expIDs, exps )
                yield iStr
            else:
                print "Probe not found:", probeName
        

        #raDbHandle.write( "INSERT into raDb( name, sampleTable, clinicalTable, columnTable, aliasTable, shortLabel) VALUES ( '%s', '%s', '%s', '%s', '%s', '%s');\n" % \
        #    ( "genomic_" + genomicName, "sample_" + sampleName, "clinical_" + clinicalNames[0], "clinical_" + clinicalNames[0] + "_colDb", "genomic_" + genomicName + "_alias", genomicName ))
		
