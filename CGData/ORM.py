
import CGData
import os
import sqlalchemy
import sqlalchemy.orm
from sqlalchemy.ext.declarative import declarative_base
import hashlib
import json

import h5py
import numpy


"""
This is an experimental module, to test design concepts 
related to treating CGData modules like ORM operators
"""

Base = declarative_base()

class cgDB(Base):
    __tablename__ = "cgDB"    
    fileID = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    type = sqlalchemy.Column(sqlalchemy.String)
    name = sqlalchemy.Column(sqlalchemy.String)
    md5 = sqlalchemy.Column(sqlalchemy.String)
    form = sqlalchemy.Column(sqlalchemy.String)
    meta = sqlalchemy.Column(sqlalchemy.Text)


class ORMTableBase:
    def __init__(self, parent, type, name):
        self.parent = parent
        self.type = type
        self.name = name


class ORMMatrixBase(CGData.CGDataMatrixObject):
    def __init__(self, parent, f):
        self.parent = parent
        self.fileInfo = f
        self.update( json.loads(f.meta) )
        self.table = self.parent.metadata.tables[ self.fileInfo.type ]
    
    def get_col_count(self):
        sess = self.parent.session_maker()
        #sess.query( 
    


class ORMTypeSet:
    def __init__(self, parent, type):
        self.type = type
        self.parent = parent
    
    def __iter__(self):
        sess = self.parent.session_maker()
        for a in sess.query(cgDB).filter(cgDB.type == self.type).all():
            yield a.name
    
    def __getitem__(self, name):
        sess = self.parent.session_maker()
        f = sess.query(cgDB).filter( sqlalchemy.and_( cgDB.type == self.type , cgDB.name == name ) ).first()
        if f is not None:
            if f.form == "matrix":
                return ORMMatrixBase(self.parent, f)
            
    

class ORM(object):
    def __init__(self, path):
        self.path = path
        self.engine = sqlalchemy.create_engine('sqlite:///%s.sqlite' % (path),
                       echo=False)
        self.metadata = sqlalchemy.MetaData(bind=self.engine)
        Base.metadata.bind = self.engine
        self.fileTable = cgDB.__table__
        self.session_maker = sqlalchemy.orm.sessionmaker(bind=self.engine)

        if not self.fileTable.exists():
            self.fileTable.create()
        
        self.h5 = h5py.File('%s.hdf5' % (path))
    
    def factory(self, obj):
        
        if obj.__format__['name'] in self.metadata.tables:
            return self.metadata.tables[ obj.__format__['name'] ]
        else:
            
            if obj.__format__['form'] == 'table':
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
                return sqlalchemy.Table( *a )
            if obj.__format__['form'] == 'matrix':
                a = [
                    obj.__format__['name'], 
                    self.metadata, 
                    sqlalchemy.Column('fileID', sqlalchemy.Integer),
                    sqlalchemy.Column('name', sqlalchemy.String), 
                    sqlalchemy.Column('axis', sqlalchemy.Integer),
                    sqlalchemy.Column('pos', sqlalchemy.Integer)
                ]
                return sqlalchemy.Table( *a )

    def __iter__(self):
        return self.get_type_list()
    
    def __getitem__(self, item):
        return ORMTypeSet(self,item)
    
    def get_type_list(self):
        sess = self.session_maker()
        for row in sess.query( sqlalchemy.distinct(cgDB.type) ).all():
            yield row[0]
        
        
    
    def write(self, obj):
        
        table = self.factory(obj)
        if table is not None:
            if not table.exists():
                table.create()
            sess = self.session_maker()
            #self.metadata.create_all(self.engine)
            fileRecord = None
            for row in sess.query( cgDB ).filter(
                sqlalchemy.and_(
                    cgDB.type == obj.__format__['name'],
                    cgDB.name == obj.get_name()
                )
            ).all():
                print "found", row
                fileRecord = row
            if fileRecord is None:
                fileRecord = cgDB()     
                fileRecord.type = obj.__format__['name']
                fileRecord.name = obj.get_name()    
                fileRecord.meta = json.dumps(obj)
                fileRecord.form = obj.__format__['form']
                sess.add( fileRecord )
                sess.flush()
                print "inserted", fileRecord.fileID
                
            fDigest = ""
            if os.path.exists(obj.path):
                m = hashlib.md5()
                handle = open(obj.path)
                while 1:
                    buff = handle.read(10240)
                    if len(buff) == 0:
                        break
                    m.update(buff)
                fDigest = m.hexdigest()
                handle.close()
            
            if fDigest == fileRecord.md5:
                print "skipping"
            else:                
                print "fileChange"
                sess.execute( table.delete( table.c.fileID == fileRecord.fileID ) )
                #if obj.__format__['form'] == 'matrix':
                #    self.h5.delete( "/%s/%s" % (obj.__format__['name'], obj.get_name()) )
                fileRecord.md5 = ""
                sess.flush()            
            
                
                print "fileID", fileRecord.fileID
                print table
                if obj.get_type() not in self.h5:
                    self.h5.create_group(obj.get_type())
                
                if obj.__format__['form'] == 'table':
                    obj.load()
                    for row in obj.row_iter():
                        a = {}
                        for c in obj.__format__['columnDef']:
                            a[c] = getattr(row, c)
                        #print a
                        sess.execute( table.insert(a) )
                    obj.unload()
                
                if obj.__format__['form'] == 'matrix':
                    count = 0
                    obj.load()
                    for row in obj.get_row_list():
                        rowNum = obj.get_row_pos(row)                    
                        a = { 'fileID' : fileRecord.fileID, 'name' : row, 'axis' : 0, 'pos' : rowNum }
                        sess.execute( table.insert(a) )
                        count += 1
                        if count % 1000 == 0:
                            sess.flush()
                        
                    for col in obj.get_col_list():
                        colNum = obj.get_col_pos(col)                    
                        a = { 'fileID' : fileRecord.fileID, 'name' : row, 'axis' : 1, 'pos' : colNum }
                        sess.execute( table.insert(a) )
                        count += 1
                        if count % 1000 == 0:
                            sess.flush()
                    
                    dsetName = "/%s/%s" % (obj.get_type(), obj.get_name())
                    if dsetName not in self.h5:
                        if obj.__format__['valueType'] == 'float':                            
                            dset = self.h5.create_dataset(dsetName, (obj.get_row_count(), obj.get_col_count()), 'f')
                        if obj.__format__['valueType'] == 'str':                            
                            dset = self.h5.create_dataset(dsetName, (obj.get_row_count(), obj.get_col_count()), h5py.new_vlen(str))
                    else:
                        dset = self.h5[dsetName]
                    for row in obj.get_row_list():
                        d = obj.get_row(row)
                        for i in range(len(d)):
                            if d[i] is None:
                                d[i] = numpy.nan
                        dset[ obj.get_row_pos(row) ] = d

                    obj.unload()
                      
                    fileRecord.md5 = fDigest
                    sess.flush()


            sess.commit()
            
       
    
    def commit(self):
        pass
        #self.engine.commit()
