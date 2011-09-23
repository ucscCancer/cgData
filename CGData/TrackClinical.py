
import CGData
import re


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
                
        matrix = self.members["clinicalMatrix"]        
        matrix.feature_type_setup()        
        features = self.members["clinicalFeature"]
        #print features
        for a in features:
            if "stateOrder" in features[a]:
                #print features[a]["stateOrder"][0]
                
                #this weird bit of code is to split on ',', but respect \,
                #if you can think of a better way, please replace this
                tmp = re.split(r'([^,]),', features[a]["stateOrder"][0])
                enums = []
                word = True
                appending = False
                e = 0
                while e < len(tmp): 
                    if word:
                        if appending:
                            enums[-1] += tmp[e]
                        else:
                            enums.append(tmp[e])
                        word = False
                    else:
                        if tmp[e] != "\\":
                            enums[-1] += tmp[e]
                            appending = False
                        else:
                            enums[-1] += ","
                            appending = True
                        word = True
                    e += 1
                
                #print tmp
                #print enums
                #print matrix.enum_map[a]
                i = 0
                for e in matrix.enum_map[a]:
                    if e in enums:
                        matrix.enum_map[a][e] = enums.index(e)
                    else:
                        matrix.enum_map[a][e] = len(enums) + i
                        i += 1
                #print matrix.enum_map[a]
                #print "-=-=-=-=-"
        for a in matrix.gen_sql(id_table, skip_feature_setup=True):
            yield a
    
