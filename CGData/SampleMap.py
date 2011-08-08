
import cgData


class sampleMap(cgData.cgDataSetObject):

    def __init__(self):
        cgData.cgDataSetObject.__init__(self)
        self.sampleHash = {}

    def read(self, handle):
        for line in handle:
            tmp = line.rstrip().split('\t')
            if not tmp[0] in self.sampleHash:
                self.sampleHash[tmp[0]] = {}
            if len(tmp) > 1:
                self.sampleHash[tmp[0]][tmp[1]] = True

    def getChildren(self, sample):
        out = {}
        for a in self.sampleHash.get(sample, {}):
            out[a] = True
            for c in self.getChildren(a):
                out[c] = True
        return out.keys()

    def genSQL(self):
        basename = os.path.join( OUT_DIR, "%s_sample_%s" % ( DATABASE_NAME, sampleInfo[ 'name' ] ) )

        lPath = reJson.sub( "", samplePath )
        if not os.path.exists( lPath ):
            return
        rHandle = open( lPath )
        read = csv.reader( rHandle, delimiter="\t" )
        targetHash = {}
        for target in read:
            targetHash[ target[0] ] = target[1]
            targetHash[ target[1] ] = None
        
        keySet = targetHash.keys()
        keySet.sort()
        
        lHandle = open( "%s.sql" % (basename), "w")
        lHandle.write("drop table if exists sample_%s;" % ( sampleInfo[ 'name' ] ) )

        lHandle.write("""
    CREATE TABLE sample_%s (
        id           int,
        sampleName   varchar(255)
    );
    """ % ( sampleInfo[ 'name' ] ) )
        
        sampleHash = {}
        for i in range( len( keySet ) ):
            lHandle.write( "INSERT INTO sample_%s VALUES( %d, '%s' );\n" % ( sampleInfo[ 'name' ], i, keySet[i] ) )
            sampleHash[  keySet[i] ] = i
        lHandle.close()
        return sampleHash
