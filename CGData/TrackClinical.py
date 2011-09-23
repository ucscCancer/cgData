
import CGData



class TrackClinical(CGData.CGMergeObject,CGData.CGSQLObject):

    typeSet = { 
        'clinicalMatrix' : True, 
        'clinicalFeature' : True
    } 

    def __init__(self):
        CGData.CGMergeObject.__init__(self)
            
    def get_name( self ):
        return "%s" % ( self.members[ "clinicalMatrix" ].get_name() )
    
    def gen_sql(self, id_table):
        CGData.log("ClincalTrack SQL " + self.get_name())
        
        yield "clinical track testing\n"
        
        matrix = self.members["clinicalMatrix"]        
        matrix.feature_type_setup()        
        features = self.members["clinicalFeature"]
        print features
        for a in features:
            if "stateOrder" in features[a]:
                tmp = features[a]["stateOrder"][0].split(',')
                i = 0
                for e in matrix.enum_map[a]:
                    if e in tmp:
                        matrix.enum_map[a][e] = tmp.index(e)
                    else:
                        matrix.enum_map[a][e] = len(tmp) + i
                        i += 1
                print tmp
                print matrix.enum_map[a]
        
        for a in matrix.gen_sql(id_table, skip_feature_setup=True):
            yield a
    
