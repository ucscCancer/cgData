


import csv
import cgData


class clinicalMatrix(cgData.cgDataMatrixObject,cgData.cgSQLObject):

    def __init__(self):
        cgData.cgDataMatrixObject.__init__(self)
        self.probeHash = {}
        self.sampleList = {}
        self.attrs = {}

    def initSchema(self):
        CREATE_colDb = """
CREATE TABLE `%s` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) default NULL,
  `shortLabel` varchar(255) default NULL,
  `longLabel` varchar(255) default NULL,
  `valField` varchar(255) default NULL,
  `tableName` varchar(255) default NULL,
  `priority` float default NULL,
  `filterType` varchar(255) default NULL,
  `visibility` varchar(255) default NULL,
  `groupName` varchar(255) default NULL,
  PRIMARY KEY  (`id`),
  KEY `name` (`name`)
);
"""
        


    def genSQL(self):
            
        colName = None
        colHash = {}
        targetSet = []
        for row in read:
            if colName is None:
                colName = row
                for name in colName[1:]:
                    colHash[ name ] = {}
            else:
                for i in range( 1, len(row) ):
                    colHash[ colName[i] ][ row[0].rstrip() ] = row[i]
                targetSet.append( row[0].rstrip() )
        handle.close()
        
        #print colHash
        
        floatMap = {}
        enumMap = {}
        for key in colHash:
            isFloat = True
            hasVal = False
            enumSet = {}
            for sample in colHash[ key ]:
                try:
                    #print colHash[ key ][ sample ]
                    value = colHash[ key ][ sample ]
                    if value != "null" and len(value):
                        hasVal = True
                        if not enumSet.has_key( value ):
                            enumSet[ value ] = len( enumSet )
                        a = float(value)
                except ValueError:
                    isFloat = False
            if hasVal:
                if isFloat:
                    floatMap[ key ] = True
                else:
                    enumMap[ key ] = enumSet
            
        #print floatMap
        #print enumMap
        
        idMap = {}
        idNum = 0
        prior = 1
        colOrder = []
        origOrder = []	

        for name in floatMap:
            idMap[ name ] = idNum
            idNum += 1	
            colName = colFix( name )
            colOrder.append( colName )
            origOrder.append( name )
            
        for name in enumMap:		
            idMap[ name ] = idNum
            idNum += 1	
            colName = colFix( name )
            colOrder.append( colName )
            origOrder.append( name )		
        
        dHandle = open( "%s.sql" % (basename), "w")
        dHandle.write("drop table if exists clinical_%s;" % ( featureInfo[ 'name' ] ) )
        dHandle.write("""
CREATE TABLE clinical_%s (
\tsampleID int""" % ( featureInfo[ 'name' ] ))
        for col in colOrder:
            if ( enumMap.has_key( col ) ):
                dHandle.write(",\n\t%s ENUM( '%s' ) default NULL" % (col, "','".join(enumMap[ col ].keys() ) ) )
            else:
                dHandle.write(",\n\t%s FLOAT default NULL" % (col) )		
        dHandle.write("""
    ) ;	
    """)
        
        for target in targetSet:
            a = []
            for col in origOrder:
                val = colHash[ col ].get( target, None )
                #print target, col, val
                if val is None or val == "null" or len(val) == 0 :
                    a.append("\N")
                else:				
                    a.append( "'" + str(val) + "'" )
            dHandle.write("INSERT INTO clinical_%s VALUES ( %d, %s );\n" % ( featureInfo[ 'name' ], sampleMap[ target ], ",".join(a) ) )
        dHandle.close()

        cHandle = open( "%s_colDb.sql" % (basename), "w" )
        cHandle.write("drop table if exists clinical_%s_colDb;" % ( featureInfo[ 'name' ] ) )
        cHandle.write( CREATE_colDb % ( "clinical_" + featureInfo[ 'name' ] + "_colDb" ) )
        """
`id` int(10) unsigned NOT NULL default '0',
`name` varchar(255) default NULL,
`shortLabel` varchar(255) default NULL,
`longLabel` varchar(255) default NULL,
`valField` varchar(255) default NULL,
`tableName` varchar(255) default NULL,
`priority` float default NULL,
`filterType` varchar(255) default NULL,
`visibility` varchar(255) default NULL,
`groupName` varchar(255) default NULL,
PRIMARY KEY  (`id`),
KEY `name` (`name`)
"""
        for name in colOrder:
            cHandle.write("INSERT INTO clinical_%s_colDb(name, shortLabel,longLabel,valField,tableName) VALUES( '%s', '%s', '%s', '%s', '%s' );\n" % \
                ( featureInfo[ 'name' ], name, name, name, name, "clinical_" + featureInfo[ 'name' ] ) )
        cHandle.close()
            
        
