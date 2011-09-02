
import CGData


class SampleMap(CGData.CGDataSetObject):

    def __init__(self):
        CGData.CGDataSetObject.__init__(self)
        self.mhash = {}

    def read(self, handle):
        for line in handle:
            tmp = line.rstrip().split('\t')
            if not tmp[0] in self.sample_hash:
                self.sample_hash[tmp[0]] = {}
            if len(tmp) > 1:
                self.sample_hash[tmp[0]][tmp[1]] = True

    def get_children(self, sample):
        out = {}
        for a in self.sample_hash.get(sample, {}):
            out[a] = True
            for c in self.get_children(a):
                out[c] = True
        return out.keys()

    def gen_sql(self):
        basename = os.path.join( OUT_DIR, "%s_sample_%s" % ( DATABASE_NAME, sample_info[ 'name' ] ) )

        lpath = reJson.sub( "", sample_path )
        if not os.path.exists( lpath ):
            return
        rhandle = open( lpath )
        read = csv.reader( rhandle, delimiter="\t" )
        target_hash = {}
        for target in read:
            target_hash[ target[0] ] = target[1]
            target_hash[ target[1] ] = None
        
        key_set = target_hash.keys()
        key_set.sort()
        
        lhandle = open( "%s.sql" % (basename), "w")
        lhandle.write("drop table if exists sample_%s;" % ( sample_info[ 'name' ] ) )

        lhandle.write("""
    CREATE TABLE sample_%s (
        id           int,
        sampleName   varchar(255)
    ) engine 'MyISAM';
    """ % ( sample_info[ 'name' ] ) )
        
        sample_hash = {}
        for i in range( len( key_set ) ):
            lhandle.write( "INSERT INTO sample_%s VALUES( %d, '%s' );\n" % ( sample_info[ 'name' ], i, key_set[i] ) )
            sample_hash[  key_set[i] ] = i
        lhandle.close()
        return sample_hash
