


import csv
import CGData
import CGData.TSVMatrix
from CGData.SQLUtil import *

CREATE_COL_DB = """
CREATE TABLE `%s` (
  `name` varchar(255) default NULL,
  `shortLabel` varchar(255) default NULL,
  `longLabel` varchar(255) default NULL,
  `valField` varchar(255) default NULL,
  `clinicalTable` varchar(255) default NULL,
  `priority` float default NULL,
  `filterType` varchar(255) default NULL,
  `visibility` varchar(255) default NULL,
  `groupName` varchar(255) default NULL,
  PRIMARY KEY  (`name`)
) engine 'MyISAM';
"""

def sortedSamples(samples):
    import os, re
    prefix = os.path.commonprefix(samples)
    plen = len(prefix)
    if re.match('^' + prefix + '[0-9]+$', samples[0]):
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
        for key in self.col_list:
            # get unique list of values by converting to a set & back.
            # also, drop null values.
            values = list(set([v for v in self.column(key) if v not in ["null", "None", "NA"] and v is not None and len(v)]))

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
    
   
    def gen_sql_heatmap(self, id_table, skip_feature_setup=False):
        CGData.log( "Writing Clinical %s SQL" % (self['name']))
        
        if not skip_feature_setup:
            self.feature_type_setup()

        table_name = self['name']

        yield "drop table if exists clinical_%s;" % ( table_name )

        yield """
CREATE TABLE clinical_%s (
\tsampleID int,
\tsampleName ENUM ('%s')""" % ( table_name, "','".join(sortedSamples(self.row_hash.keys())) )

        for col in self.col_order:
            if ( self.enum_map.has_key( col ) ):
                yield ",\n\t`%s` ENUM( '%s' ) default NULL" % (col.strip(), "','".join( sql_fix(a) for a in sorted(self.enum_map[ col ].keys(), lambda x,y: self.enum_map[col][x]-self.enum_map[col][y]) ) )
            else:
                yield ",\n\t`%s` FLOAT default NULL" % (col.strip())
        yield """
    ) engine 'MyISAM';
    """

        for target in sortedSamples(self.row_hash.keys()):
            a = []
            for col in self.orig_order:
                val = self.row_hash[ target ][ self.col_list[ col ] ]
                if val is None or val == "null" or len(val) == 0 :
                    a.append("\\N")
                else:
                    a.append( "'" + sql_fix( val.encode('string_escape') ) + "'" )
            yield u"INSERT INTO clinical_%s VALUES ( %d, '%s', %s );\n" % ( table_name, id_table.get( table_name + ':sample_id', target ), sql_fix(target), u",".join(a) )


        yield "drop table if exists clinical_%s_colDb;" % ( table_name )
        yield CREATE_COL_DB % ( "clinical_" + table_name + "_colDb" )

        yield "INSERT INTO clinical_%s_colDb(name, shortLabel,longLabel,valField,clinicalTable,filterType,visibility,priority) VALUES( '%s', '%s', '%s', '%s', '%s', '%s', 'on',1);\n" % \
                ( table_name, 'sampleName', 'sample name', 'sample name', 'sampleName', "clinical_" + table_name, 'coded' )

        i = 0;
        for name in self.col_order:
            filter = 'coded' if self.enum_map.has_key(name) else 'minMax'
            yield "INSERT INTO clinical_%s_colDb(name, shortLabel,longLabel,valField,clinicalTable,filterType,visibility,priority) VALUES( '%s', '%s', '%s', '%s', '%s', '%s', '%s',1);\n" % \
                    ( table_name, name, name, name, name, "clinical_" + table_name, filter, 'on' if i < 10 else 'off')
            i += 1
