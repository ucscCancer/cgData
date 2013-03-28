


import csv
import CGData
import CGData.TSVMatrix
from CGData.SQLUtil import *

CREATE_COL_DB = """
CREATE TABLE `%s` (
  `id` int(10) unsigned NOT NULL PRIMARY KEY AUTO_INCREMENT,
  `name` varchar(255) NOT NULL UNIQUE,
  `shortLabel` varchar(255) default NULL,
  `longLabel` varchar(255) default NULL,
  `valField` varchar(255) default NULL,
  `clinicalTable` varchar(255) default NULL,
  `priority` float default NULL,
  `filterType` varchar(255) default NULL,
  `visibility` varchar(255) default NULL,
  `groupName` varchar(255) default NULL
) engine 'MyISAM';
"""

NULL_VALUES = ['NULL', "Null", 'NA', '']

def sortedSamples(samples):
    import os, re
    # Check for numeric sample ids. Allow for a common prefix
    # before the number.
    prefix = os.path.commonprefix(samples)
    plen = len(prefix)
    if reduce(lambda x,y: x and y, map(lambda s: re.match('^' + prefix + '[0-9]+$', s), samples)):
        return sorted(samples, cmp=lambda x, y: int(x[plen:]) - int(y[plen:]))
    else:
        return sorted(samples)

class ClinicalMatrix(CGData.TSVMatrix.TSVMatrix):

    element_type = str
    corner_name = "#sample"

    def __init__(self):
        super(ClinicalMatrix, self).__init__()
        self[':clinicalFeature'] = '__null__'

    def is_link_ready(self):
        if self.get( ":sampleMap", None ) == None:
            return False
        return True


    def get_col_namespace(self):
        if self.get(":clinicalFeature", None) is not None:
            return "clinicalFeature:" + self.attrs[":clinicalFeature"]
        return None

    def get_row_namespace(self):
        if self.get(":sampleMap", None) is not None:
            return "sampleMap:" + self[":sampleMap"]
        return None

    def column(self, name):
        return [ self.row_hash[row][self.col_list[name]] for row in self.row_hash ]

    def __guess_type__(self, values):
        type = 'float'
        for value in values:
            try:
                a = float(value)
            except ValueError:
                type = 'category'
                break
        return [type]

    def feature_type_setup(self, types = {}):
        if self.light_mode:
            self.load()

        self.float_map = {}
        self.enum_map = {}

        self.enum_map['sampleName'] = dict((k,v) for k,v in zip(sortedSamples(self.row_hash.keys()), range(0,len(self.row_hash.keys()))))

        for key in self.col_list:
            # get unique list of values by converting to a set & back.
            # also, drop null values.
            values = list(set([v for v in self.column(key) if v is not None and v.upper() not in NULL_VALUES]))

            if not key in types:
                types[key] = self.__guess_type__(values)

            if len(values) > 0: # drop empty columns. XXX is this correct behavior?
                if types[key] == ['float']:
                    self.float_map[key] = True
                else:
                    self.enum_map[key] = dict((enum, order) for enum, order in zip(sorted(values), range(len(values))))

        id_map = {}
        id_num = 0
        prior = 1
        self.col_order = []
        self.orig_order = []

        for name in self.float_map:
            id_map[ name ] = id_num
            id_num += 1    
            colName = col_fix( name )
            self.col_order.append( colName )
            self.orig_order.append( name )

        for name in self.enum_map:
            id_map[ name ] = id_num
            id_num += 1    
            colName = col_fix( name )
            self.col_order.append( colName )
            self.orig_order.append( name )
    
   
    def gen_sql_heatmap(self, id_table, features=None):
        CGData.log( "Writing Clinical %s SQL" % (self['name']))
        
        if features == None:
            self.feature_type_setup()
            features = {}

        features['sampleName'] = { 'shortTitle': ['Sample name'], 'longTitle': ['Sample name'], 'visibility': ['on'], 'priority': [1] }

        table_name = self['name'].replace(".","_")
        clinical_table = 'clinical_' + table_name

        yield "DROP TABLE IF EXISTS %s;\n" % ( clinical_table )
        yield "DELETE codes FROM codes, colDb WHERE codes.feature = colDb.id AND colDb.clinicalTable = '%s';\n" % clinical_table
        yield "DELETE FROM colDb WHERE clinicalTable = '%s';\n" % clinical_table

        # colDb
        i = 0;
        for name in self.col_order:
            shortLabel = name if name not in features or 'shortTitle' not in features[name] else features[name]['shortTitle'][0]
            longLabel = name if name not in features or 'longTitle' not in features[name] else features[name]['longTitle'][0]
            filter = 'coded' if self.enum_map.has_key(name) else 'minMax'
            visibility = ('on' if i < 10 else 'off') if name not in features or 'visibility' not in features[name] else features[name]['visibility'][0]
            priority = 1 if name not in features or 'priority' not in features[name] else float(features[name]['priority'][0])
            yield "INSERT INTO colDb(name, shortLabel,longLabel,valField,clinicalTable,filterType,visibility,priority) VALUES( '%s', '%s', '%s', '%s', '%s', '%s', '%s', %f);" % \
                    ( sql_fix(name), sql_fix(shortLabel), sql_fix(longLabel), sql_fix(name), clinical_table, filter, visibility, priority)
            yield "SET @col%d=LAST_INSERT_ID();\n" % i
            i += 1

        # codes
        i = 0;
        values = {}
        for col in self.col_order:
            if ( self.enum_map.has_key( col ) ):
                values[col] = {}
                j = 0
                for a in sorted(self.enum_map[ col ].keys(), lambda x,y: self.enum_map[col][x]-self.enum_map[col][y]):
                    yield "INSERT INTO codes(feature,ordering,value) VALUES (@col%d, %d, '%s'); SET @val%d_%d=LAST_INSERT_ID();\n" % (i, j, sql_fix(a), i, j)
                    values[col][a] = "@val%d_%d" % (i, j)
                    j += 1
            i += 1


        yield "CREATE TABLE %s (sampleID INT NOT NULL UNIQUE" % clinical_table

        for col in self.col_order:
            if col == 'sampleName':
                yield ",\n\tsampleName INT UNSIGNED NOT NULL UNIQUE"
            else:
                if self.enum_map.has_key(col):
                    yield ",\n\t`%s` INT UNSIGNED DEFAULT NULL" % (col.strip())
                else:
                    yield ",\n\t`%s` FLOAT DEFAULT NULL" % (col.strip())
        yield """
    ) engine 'MyISAM';
    """

        for target in sortedSamples(self.row_hash.keys()):
            a = []
            for col,orig in zip(self.col_order, self.orig_order):
                if col == 'sampleName':
                    val = target
                else:
                    val = self.row_hash[ target ][ self.col_list[ orig ] ]
                if val is None or val.upper() in NULL_VALUES:
                    a.append("\\N")
                else:
                    if col in self.enum_map:
                        a.append(values[col][val])
                    else:
                        a.append(val)
            yield u"INSERT INTO %s VALUES ( %d, %s );\n" % ( clinical_table, id_table.get( table_name + ':sample_id', target ), u",".join(a) )
