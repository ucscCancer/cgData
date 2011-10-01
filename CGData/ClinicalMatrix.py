


import csv
import CGData
import CGData.TSVMatrix
from CGData.SQLUtil import *

CREATE_COL_DB = """
CREATE TABLE `%s` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) default NULL,
  `shortLabel` varchar(255) default NULL,
  `longLabel` varchar(255) default NULL,
  `valField` varchar(255) default NULL,
  `clinicalTable` varchar(255) default NULL,
  `priority` float default NULL,
  `filterType` varchar(255) default NULL,
  `visibility` varchar(255) default NULL,
  `groupName` varchar(255) default NULL,
  PRIMARY KEY  (`id`),
  KEY `name` (`name`)
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

class ClinicalMatrix(CGData.TSVMatrix.TSVMatrix,CGData.CGSQLObject):
    
    element_type = str
    corner_name = "#sample"

    def __init__(self):
        CGData.TSVMatrix.TSVMatrix.__init__(self)

    def init_schema(self):
        pass
        
    def is_link_ready(self):
        if self.attrs.get( ":sampleMap", None ) == None:
            return False
        return True


    def get_x_namespace(self):
        if self.attrs.get(":clinicalFeature", None) is not None:
            return "clinicalFeature:" + self.attrs[":clinicalFeature"]
        return None

    def get_y_namespace(self):
        if self.attrs.get(":sampleMap", None) is not None:
            return "sampleMap:" + self.attrs[":sampleMap"]
        return None
    
    def feature_type_setup(self):
        if self.light_mode:
            self.load()
            
        self.float_map = {}
        self.enum_map = {}
        for key in self.col_list:
            col = self.col_list[key]
            is_float = True
            has_val = False
            enum_set = {}
            for row in self.row_hash:
                try:
                    #print colHash[ key ][ sample ]
                    value = self.row_hash[ row ][ col ]
                    if value not in ["null", "None", "NA"] and value is not None and len(value):
                        has_val = True
                        if not enum_set.has_key( value ):
                            enum_set[ value ] = len( enum_set )
                        a = float(value)
                except ValueError:
                    is_float = False
            if has_val:
                if is_float:
                    self.float_map[ key ] = True
                else:
                    self.enum_map[ key ] = enum_set
            
        #print float_map
        #print enum_map
        
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
    
   
    def gen_sql(self, id_table, skip_feature_setup=False):
        CGData.log( "Gen %s SQL" % (self.attrs['name']))
        
        if not skip_feature_setup:
            self.feature_type_setup()

        table_name = self.attrs['name']

        yield "drop table if exists clinical_%s;" % ( table_name )

        yield """
CREATE TABLE clinical_%s (
\tsampleID int,
\tsampleName ENUM ('%s')""" % ( table_name, "','".join(sortedSamples(self.row_hash.keys())) )

        for col in self.col_order:
            if ( self.enum_map.has_key( col ) ):
                yield ",\n\t`%s` ENUM( '%s' ) default NULL" % (col.strip(), "','".join( sql_fix(a) for a in self.enum_map[ col ].keys() ) )
            else:
                yield ",\n\t`%s` FLOAT default NULL" % (col.strip())
        yield """
    ) engine 'MyISAM';
    """

        for target in sortedSamples(self.row_hash.keys()):
            a = []
            for col in self.orig_order:
                val = self.row_hash[ target ][ self.col_list[ col ] ]
                #print target, col, val
                if val is None or val == "null" or len(val) == 0 :
                    a.append("\\N")
                else:
                    #a.append( "'" + sql_fix(val) + "'" )
                    a.append( "'" + sql_fix( val.encode('string_escape') ) + "'" )
            yield u"INSERT INTO clinical_%s VALUES ( %d, '%s', %s );\n" % ( table_name, id_table.get( 'sample_id', target ), sql_fix(target), u",".join(a) )
            #yield u"INSERT INTO clinical_%s VALUES ( %d, %s );\n" % ( table_name, id_table.get( 'sample_id', target ), u",".join(a) )


        yield "drop table if exists clinical_%s_colDb;" % ( table_name )
        yield CREATE_COL_DB % ( "clinical_" + table_name + "_colDb" ) 
        """
`id` int(10) unsigned NOT NULL default '0',
`name` varchar(255) default NULL,
`shortLabel` varchar(255) default NULL,
`longLabel` varchar(255) default NULL,
`valField` varchar(255) default NULL,
`clinicalTable` varchar(255) default NULL,
`priority` float default NULL,
`filterType` varchar(255) default NULL,
`visibility` varchar(255) default NULL,
`groupName` varchar(255) default NULL,
PRIMARY KEY  (`id`),
KEY `name` (`name`)
"""
        yield "INSERT INTO clinical_%s_colDb(name, shortLabel,longLabel,valField,clinicalTable,filterType,visibility,priority) VALUES( '%s', '%s', '%s', '%s', '%s', '%s', 'on',1);\n" % \
                ( table_name, 'sampleName', 'sample name', 'sample name', 'sampleName', "clinical_" + table_name, 'coded' )

        i = 0;
        for name in self.col_order:
            filter = 'coded' if self.enum_map.has_key(name) else 'minMax'
            yield "INSERT INTO clinical_%s_colDb(name, shortLabel,longLabel,valField,clinicalTable,filterType,visibility,priority) VALUES( '%s', '%s', '%s', '%s', '%s', '%s', '%s',1);\n" % \
                    ( table_name, name, name, name, name, "clinical_" + table_name, filter, 'on' if i < 10 else 'off')
            i += 1



