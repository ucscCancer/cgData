
import CGData

import sqlalchemy
import sqlalchemy.orm

"""
This is an experimental module, to test design concepts 
related to treating CGData modules like ORM operators
"""


def get_session():
    return Session()


class Session(object):
    def __init__(self):
        self.engine = sqlalchemy.create_engine('sqlite:///test.db',
                       echo=True)
        self.metadata = sqlalchemy.MetaData(bind=self.engine)
        
        self.fileTable = sqlalchemy.Table('cgDB', self.metadata,
            sqlalchemy.Column('fileID', sqlalchemy.Integer, primary_key=True),
            sqlalchemy.Column('type', sqlalchemy.String ),
            sqlalchemy.Column('name', sqlalchemy.String )
        )
        if not self.fileTable.exists():
            self.fileTable.create()
        
    
    def factory(self, obj):
        
        if obj.__format__['name'] in self.metadata.tables:
            obj.table = self.metadata.tables[ obj.__format__['name'] ]
        else:
            a = [
                obj.__format__['name'], 
                self.metadata, 
                sqlalchemy.Column('fileID', sqlalchemy.Integer)
            ]
            print obj.__format__['columnDef']
            for c in obj.__format__['columnDef']:
                col = None
                print c
                colType = None
                if 'columnType' in obj.__format__:
                    colType = sqlalchemy.String
                else:
                    colType = sqlalchemy.String
                
                col = sqlalchemy.Column(c, colType)
                if col is not None:
                    a.append(col)
            obj.table = sqlalchemy.Table( *a )
    
    def write(self, obj):
        if obj.__format__['form'] == 'table':
            self.factory(obj)
            if not obj.table.exists():
                obj.table.create()
            Session = sqlalchemy.orm.sessionmaker(bind=self.engine)
            sess = Session()
            #self.metadata.create_all(self.engine)
            if sess.query( 
                sqlalchemy.and_( 
                    self.fileTable.c.type == obj.__format__['name'],
                    self.fileTable.c.name == obj.get_name()
                )
            ).count() >= 1:
                print "already loaded"
            
            sess.execute( self.fileTable.insert( 
                { 'name' : obj.get_name(), 
                'type' : obj.__format__['name']
                }
            ))
            
            print self.fileTable.auto_increment

            """

            print obj.table
            for row in obj.row_iter():
                a = {}
                for c in obj.__format__['columnDef']:
                    a[c] = getattr(row, c)
                #print a
                sess.execute( obj.table.insert(a) )
            sess.commit()
            """
            
       
    
    def commit(self):
        pass
        #self.engine.commit()
