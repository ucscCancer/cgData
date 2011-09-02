


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

class ClinicalMatrix(CGData.TSVMatrix.TSVMatrix,CGData.CGSQLObject):
    
    element_type = str

    def __init__(self):
        CGData.TSVMatrix.TSVMatrix.__init__(self)

    def init_schema(self):
		pass
        
    def is_link_ready(self):
        if self.attrs.get( ":sampleMap", None ) == None:
            return False
        return True
        
    def build_ids(self, id_allocator):
        if self.light_mode:
            self.load()
            
        sample_list = self.get_rows()
        
        for sample_id in sample_list:
            id_allocator.alloc( 'sample_id', sample_id )

        feature_list = self.get_cols()
        for feature_id in feature_list:
            id_allocator.alloc( 'feature_id', sample_id )

    def gen_sql(self, id_table):
        CGData.log( "Gen %s SQL" % (self.attrs['name']))
        float_map = {}
        enum_map = {}
        for key in self.col_list:
            col = self.col_list[ key ]
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
                    float_map[ key ] = True
                else:
                    enum_map[ key ] = enum_set
            
        #print float_map
        #print enum_map
        
        id_map = {}
        id_num = 0
        prior = 1
        col_order = []
        orig_order = []	

        for name in float_map:
            id_map[ name ] = id_num
            id_num += 1	
            colName = col_fix( name )
            col_order.append( colName )
            orig_order.append( name )
            
        for name in enum_map:		
            id_map[ name ] = id_num
            id_num += 1	
            colName = col_fix( name )
            col_order.append( colName )
            orig_order.append( name )		
        
        table_name = self.attrs['name']
        
        yield "drop table if exists clinical_%s;" % ( table_name )
        
        yield """
CREATE TABLE clinical_%s (
\tsampleID int""" % ( table_name )

        for col in col_order:
            if ( enum_map.has_key( col ) ):
                yield ",\n\t`%s` ENUM( '%s' ) default NULL" % (col.strip(), "','".join( sql_fix(a) for a in enum_map[ col ].keys() ) )
            else:
                yield ",\n\t`%s` FLOAT default NULL" % (col.strip())
        yield """
    ) engine 'MyISAM';
    """
        
        for target in self.row_hash:
            a = []
            for col in orig_order:
                val = self.row_hash[ target ][ self.col_list[ col ] ]
                #print target, col, val
                if val is None or val == "null" or len(val) == 0 :
                    a.append("\\N")
                else:				
                    a.append( "'" + sql_fix( val.encode('string_escape') ) + "'" )
            yield u"INSERT INTO clinical_%s VALUES ( %d, %s );\n" % ( table_name, id_table.get( 'sample_id', target ), u",".join(a) )


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
        for name in col_order:
            filter = 'coded' if enum_map.has_key(name) else 'minMax'
            yield "INSERT INTO clinical_%s_colDb(name, shortLabel,longLabel,valField,clinicalTable,filterType,visibility,priority) VALUES( '%s', '%s', '%s', '%s', '%s', '%s', 'on',1);\n" % \
                    ( table_name, name, name, name, name, "clinical_" + table_name, filter )

            
        
