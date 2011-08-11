

class CancerTrack:
    
    if includeList is not None and not includeList.has_key( genomeInfo[ 'name' ] ):
            return 
        print "probe mapping", genomicPath, "  ", probePath
        basename = os.path.join( OUT_DIR, "%s_genomic_%s" % ( DATABASE_NAME, genomeInfo[ 'name' ] ) )
        print basename
        rPath = reJson.sub( "", probePath )
        lPath = reJson.sub( "", genomicPath )
        if not os.path.exists( rPath ) or not os.path.exists( lPath ):
            return
        rHandle = open( rPath )
        read = csv.reader( rHandle, delimiter="\t" )
        probeHash = {}
        for line in read:
            probeHash[ line[0] ] = { 'chrom' : line[1], 'start' : line[2], 'end' : line[3], 'strand' : line[4], 'alias' : line[5].split(',') }
        rHandle.close()
        
        lHandle = open( lPath )
        read = csv.reader( lHandle, delimiter="\t")
        oHandle = open( "%s.sql" % (basename), "w" )
        oHandle.write("drop table if exists genomic_%s;" % ( genomeInfo[ 'name' ] ) )
        oHandle.write( CREATE_BED % ( "genomic_" + genomeInfo[ 'name' ]  ) )
        
        head = None
        for line in read:
            if head is None:
                head = line
            else:
                probe = line[0]
                sampleIDs = []
                for a in head[1:]:
                    try:
                        sampleIDs.append( str(sampleMap[a]) )
                    except KeyError:
                        error( "UNKNOWN SAMPLE: %s" % (a) )
                        sampleIDs = None
                        break
                    
                if sampleIDs is not None:
                    expIDs = ','.join( sampleIDs )
                    exps = ','.join( str(a) for a in line[1:])
                    try:
                        iStr = "insert into %s(chrom, chromStart, chromEnd, strand,  name, expCount, expIds, expScores) values ( '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s' );\n" % \
                        ( "genomic_%s" % (genomeInfo[ 'name' ]), probeHash[probe]['chrom'], probeHash[probe]['start'], probeHash[probe]['end'], probeHash[probe]['strand'], probe, len(line), expIDs, exps )
                        oHandle.write( iStr )
                    except KeyError:
                        error( "MISSING PROBE: %s" % ( probe ) )
        oHandle.close()
    
        handle = open( rPath )
        read = csv.reader( handle, delimiter="\t" )
        
        oHandle = open( "%s_alias.sql" % (basename), "w" )
        oHandle.write("drop table if exists genomic_%s_alias;" % ( genomeInfo[ 'name' ] ) )
        oHandle.write("""
CREATE TABLE genomic_%s_alias (
\tname varchar(255) default NULL,
\talias varchar(255) default NULL
);
""" % ( genomeInfo[ 'name' ] ) )
        for row in read:
            for alias in row[5].rstrip().split(','):
                if len(alias):
                    oHandle.write("INSERT into genomic_%s_alias values ( '%s', '%s' );\n" % (genomeInfo[ 'name' ], sqlFix(row[0]), sqlFix(alias) ) ) 
        handle.close()
        oHandle.close()
