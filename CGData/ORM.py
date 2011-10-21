
import CGData

import sqlalchemy
import sqlalchemy.orm

def get_session():
    return Session()
    
class Session(object):
    def __init__(self):
        self.engine = sqlalchemy.create_engine('sqlite:///test.db',
                       echo=True)
        self.metadata = sqlalchemy.MetaData(bind=self.engine)
    
    def factory(self, obj):
    
        a = [
            obj.get_name(), 
            self.metadata
        ]
        print obj.COLS
        for c in obj.COLS:
            col = None
            print c.name
            if c.type == str:
                col = sqlalchemy.Column(c.name, sqlalchemy.String, primary_key=c.primary_key)
            if c.type == int:
                col = sqlalchemy.Column(c.name, sqlalchemy.Integer, primary_key=c.primary_key)
            if col is not None:
                a.append(col)
        obj.table = sqlalchemy.Table( *a )
        obj.row_class = type( 'row_class', (object,), {} )
        #sqlalchemy.orm.mapper(obj.row_class, obj.table) 
    
    def write(self, obj):
        if obj.DATA_FORM == CGData.TABLE:
            self.factory(obj)
            obj.table.create()
            #self.metadata.create_all(self.engine)
            print obj.table
            Session = sqlalchemy.orm.sessionmaker(bind=self.engine)
            sess = Session()
            for row in obj.row_iter():
                a = {}
                i = 0
                for c in obj.COLS:
                    a[c.name] = row[i]
                    i += 1
                #print a
                sess.execute( obj.table.insert(a) )
            sess.commit()
            
            
        """
        print obj.get_name(), obj.DATA_FORM
        if obj.DATA_FORM == CGData.TABLE:
            names = []
            types = []
            o = "create table '%s' (\n " % (obj.get_name())
            s = []
            for c in obj.COLS:
                si = "\t'%s' %s default NULL" % (c.name, c.type)
                s.append(si)
            o += ",\n".join(s)
            o += "\n);"
            print o
        """            
    
    def commit(self):
        pass
        #self.engine.commit()
