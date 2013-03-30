import CGData
import re
import csv


class TrackClinical(CGData.CGMergeObject):

    DATA_FORM = None

    typeSet = { 
        'clinicalMatrix' : True, 
        'clinicalFeature' : True
    } 

    def __init__(self):
        CGData.CGMergeObject.__init__(self)
            
    def get_name( self ):
        return "%s" % ( self.members[ "clinicalMatrix" ].get_name() )
    
    def gen_sql_heatmap(self, id_table, opts):
        CGData.log("ClincalTrack SQL " + self.get_name())

        features = self.members["clinicalFeature"].features
        matrix = self.members["clinicalMatrix"]

        # e.g. { 'HER2+': 'category', ...}
        explicit_types = dict((f, features[f]['valueType']) for f in features if 'valueType' in features[f])

        matrix.feature_type_setup(explicit_types)
        for a in self.members['clinicalMatrix'].col_list:
            if a in features and "stateOrder" in features[a]:

                enums = [x for x in csv.reader(features[a]["stateOrder"], skipinitialspace=True)][0]
                i = 0
                #do not drop states in stateOrder
                for e in enums:
                    matrix.enum_map[a][e] = enums.index(e)

                for e in matrix.enum_map[a]:
                    if e in enums:
                        matrix.enum_map[a][e] = enums.index(e)
                    else:
                        matrix.enum_map[a][e] = len(enums) + i
                        i += 1
        for a in matrix.gen_sql_heatmap(id_table, features=features):
            yield a
