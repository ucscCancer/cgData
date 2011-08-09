


import csv
import CGData
import CGData.TSVMatrix
from CGData.SQLUtil import *

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

class ClinicalMatrix(CGData.TSVMatrix.TSVMatrix,CGData.cgSQLObject):
    
    elementType = str

    def __init__(self):
        CGData.TSVMatrix.TSVMatrix.__init__(self)

    def initSchema(self):
		pass
        
    def isLinkReady(self):
        if self.attrs.get( ":sampleMap", None ) == None:
            return False
        return True
        
    def buildIDs(self, idAllocator):
        if self.lightMode:
            self.load()
            
        sampleList = self.getRows()
        
        for sampleID in sampleList:
            idAllocator.alloc( 'sampleID', sampleID )

        featureList = self.getCols()
        for featureID in featureList:
            idAllocator.alloc( 'featureID', sampleID )

    def genSQL(self, idTable):
        floatMap = {}
        enumMap = {}
        for key in self.colList:
            col = self.colList[ key ]
            isFloat = True
            hasVal = False
            enumSet = {}
            for row in self.rowHash:
                try:
                    #print colHash[ key ][ sample ]
                    value = self.rowHash[ row ][ col ]
                    if value not in ["null", "None", "NA"] and value is not None and len(value):
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
        
        tableName = self.attrs['name']
        
        yield "drop table if exists clinical_%s;" % ( tableName )
        
        yield """
CREATE TABLE clinical_%s (
\tsampleID int""" % ( tableName )

        for col in colOrder:
            if ( enumMap.has_key( col ) ):
                yield ",\n\t%s ENUM( '%s' ) default NULL" % (col, "','".join( sqlFix(a) for a in enumMap[ col ].keys() ) )
            else:
                yield ",\n\t%s FLOAT default NULL" % (col)
        yield """
    ) ;	
    """
        
        for target in self.rowHash:
            a = []
            for col in origOrder:
                val = self.rowHash[ target ][ self.colList[ col ] ]
                #print target, col, val
                if val is None or val == "null" or len(val) == 0 :
                    a.append("\N")
                else:				
                    a.append( "'" + sqlFix( str(val) ) + "'" )
            yield "INSERT INTO clinical_%s VALUES ( %d, %s );\n" % ( tableName, idTable.get( 'sampleID', target ), ",".join(a) )


        yield "drop table if exists clinical_%s_colDb;" % ( tableName )
        yield CREATE_colDb % ( "clinical_" + tableName + "_colDb" ) 
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
            yield "INSERT INTO clinical_%s_colDb(name, shortLabel,longLabel,valField,tableName) VALUES( '%s', '%s', '%s', '%s', '%s' );\n" % \
                ( tableName, name, name, name, name, "clinical_" + tableName )

            
        
