
import CGData
import CGData.DataSet
import os
import sqlalchemy
import sqlalchemy.orm
from sqlalchemy import and_
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
    meta = sqlalchemy.Column(sqlalchemy.Text)

class cgLink(Base):
    __tablename__ = "cgLink"
    linkID = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    src_file = sqlalchemy.Column(sqlalchemy.Integer)
    dst_file = sqlalchemy.Column(sqlalchemy.Integer)
    predicate = sqlalchemy.Column(sqlalchemy.String)
    
    def __init__(self, src_file, dst_file, predicate):
        self.src_file = src_file
        self.dst_file = dst_file
        self.linkID = "%s_%s" % (src_file, dst_file)
        self.predicate = predicate

class ORMTableBase(CGData.CGObjectBase):
    def __init__(self, parent, f):
        self.parent = parent
        self.fileInfo = f
        self.update( json.loads(f.meta) )
        self.table = self.parent.get_format_table( self.__format__ )

class ORMMatrixBase(CGData.CGDataMatrixObject):
    def __init__(self, parent, f):
        self.parent = parent
        self.fileInfo = f
        self.update( json.loads(f.meta) )
        self.__format__ = json.loads(f.format)
        self.table = self.parent.get_format_table( self.__format__ )
        self.dataset = self.parent.h5[ "/%s/%s" % (f.type, f.name) ]
                
        self.col_map = {}        
        for e in self.sess.query( self.table.c.name, self.table.c.pos ).filter( and_( self.table.c.fileID == self.fileInfo.fileID, self.table.c.axis==1 ) ).all():
            self.col_map[e[0]] = e[1]

        self.row_map = {}        
        for e in self.sess.query( self.table.c.name, self.table.c.pos ).filter( and_( self.table.c.fileID == self.fileInfo.fileID, self.table.c.axis==0 ) ).all():
            self.row_map[e[0]] = e[1]
        
        
    
    def get_col_count(self):
       return len(self.col_map)

    def get_col_list(self):
        """
        Returns names of columns
        """
        out = self.col_map.keys()
        out.sort( lambda x,y: self.col_map[x]-self.col_map[y])
        return out 
        
    def get_row_list(self):
        """
        Returns names of rows
        """
        out = self.row_map.keys()
        out.sort( lambda x,y: self.row_map[x]-self.row_map[y])
        return out 

    def get_col(self, col_name):
        return self.dataset[:, self.col_map[col_name] ]
    
    def get_row(self, row_name):
        return self.dataset[self.row_map[row_name], : ]
    
    def get_row_map(self):
        return self.row_map

    def get_col_map(self):
        return self.col_map


class ORMTypeSet:
    def __init__(self, parent, type):
        self.type = type
        self.parent = parent
    
    def __iter__(self):
        for a in self.sess.query(cgDB).filter(cgDB.type == self.type).all():
            yield a.name
    
    def __getitem__(self, name):
        f = self.sess.query(cgDB).filter( sqlalchemy.and_( cgDB.type == self.type , cgDB.name == name ) ).first()
        if f is not None:
            format = json.loads(f.format)
            if format['form'] == "matrix":
                return ORMMatrixBase(self.parent, f)
            if format['form'] == "table":
                return ORMTableBase(self.parent, f)
            
    

class ORM(CGData.DataSet.DataSetBase):
    def __init__(self, path, options={}):
        self.path = path
        self.options = options
        self.engine = sqlalchemy.create_engine('sqlite:///%s.sqlite' % (path),
                       echo=False)
        self.metadata = sqlalchemy.MetaData(bind=self.engine)
        Base.metadata.bind = self.engine
        self.fileTable = cgDB.__table__
        self.linkTable = cgLink.__table__
        self.session_maker = sqlalchemy.orm.sessionmaker(bind=self.engine)
        self.sess = self.session_maker()

        if not self.fileTable.exists():
            self.fileTable.create()

        if not self.linkTable.exists():
            self.linkTable.create()

        if self.options.get('storeMatrix', True):
            self.h5 = h5py.File('%s.hdf5' % (path))
    
    def get_format_table(self, format):
        
        if format['name'] in self.metadata.tables:
            return self.metadata.tables[ format['name'] ]
        else:
            
            if format['form'] == 'table':
                a = [
                    format['name'], 
                    self.metadata, 
                    sqlalchemy.Column('fileID', sqlalchemy.Integer)
                ]
                for c in format['columnOrder']:
                    col = None
                    print c
                    colType = None
                    if 'columnType' in format:
                        colType = sqlalchemy.String
                    else:
                        colType = sqlalchemy.String
                    
                    col = sqlalchemy.Column(c, colType)
                    if col is not None:
                        a.append(col)
                return sqlalchemy.Table( *a )
            if format['form'] == 'matrix':
                a = [
                    format['name'], 
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
    
    def add_all(self, ds):
        for t in ds:
            for name in ds[t]:
                try:
                    if not self.loaded( ds[t][name].path, md5Check=False ):
                        print "Storing ", t, name 
                        self.write( ds[t][name] )
                    ds[t][name].unload()
                except IOError as e:
                    print e
        self.commit()



    def get_type_list(self):
        for row in self.sess.query( sqlalchemy.distinct(cgDB.type) ).all():
            yield row[0]
        
    
    def md5check(self, path):
        fDigest = ""
        if os.path.exists(path):
            m = hashlib.md5()
            handle = open(path)
            while 1:
                buff = handle.read(10240)
                if len(buff) == 0:
                    break
                m.update(buff)
            fDigest = m.hexdigest()
            handle.close()
    
    def loaded( self, path, md5Check=False ):
        obj = CGData.light_load(path)
        for row in self.sess.query( cgDB ).filter(
                sqlalchemy.and_(
                    cgDB.type == obj.__format__['name'],
                    cgDB.name == obj.get_name()
                )
        ).all():
            print "found", row
            fileRecord = row
            if not md5Check:
                return True            
            fDigest = self.md5check(path)            
            if fDigest == fileRecord.md5:
                return True
        return False
    
    def get_or_create_filerecord(self, file_type, file_name):
        #self.metadata.create_all(self.engine)
        fileRecord = None
        for row in self.sess.query( cgDB ).filter(
            sqlalchemy.and_(
                cgDB.type == file_type,
                cgDB.name == file_name
            )
        ).all():
            fileRecord = row
        if fileRecord is None:
            fileRecord = cgDB()     
            fileRecord.type = file_type
            fileRecord.name = file_name    
            self.sess.add( fileRecord )
            self.sess.flush()
        return fileRecord

    def write(self, obj):        
        table = self.get_format_table(obj.__format__)
        if table is not None:
            if not table.exists():
                table.create()
            #self.metadata.create_all(self.engine)
            fileRecord = self.get_or_create_filerecord( obj.__format__['name'], obj.get_name() )

            fileRecord.meta = json.dumps(obj)
            lmap = obj.get_link_map()
            for pred in lmap:
                print lmap
                other = self.get_or_create_filerecord( lmap[pred]['type'], lmap[pred]['name'] )
                link = cgLink( fileRecord.fileID, other.fileID, pred )
                self.sess.add( link )
            self.sess.flush()
            self.sess.execute( table.delete( table.c.fileID == fileRecord.fileID ) )
            
            
            
            #if obj.__format__['form'] == 'matrix':
            #    self.h5.delete( "/%s/%s" % (obj.__format__['name'], obj.get_name()) )
            fileRecord.md5 = ""
            self.sess.flush()        
            
            print "fileID", fileRecord.fileID
            print table
            
            if obj['cgformat']['form'] == 'table':
                obj.load()
                for row in obj.row_iter():
                    a = {}
                    for c in obj.__format__['columnOrder']:
                        a[c] = getattr(row, c)
                    #print a
                    self.sess.execute( table.insert(a) )
                obj.unload()
            
            if obj['cgformat']['form'] == 'matrix':
                count = 0
                storeMatrix = self.options.get('storeMatrix', True)
                if storeMatrix:
                    obj.load()

                for row in obj.load_keyset("rowKeySrc"):
                    rowNum = None
                    if storeMatrix:
                        rowNum = obj.get_row_pos(row)                    
                    a = { 'fileID' : fileRecord.fileID, 'name' : row, 'axis' : 0, 'pos' : rowNum }
                    self.sess.execute( table.insert(a) )
                    count += 1
                    if count % 1000 == 0:
                        self.sess.flush()
                    
                for col in obj.load_keyset("columnKeySrc"):
                    colNum = None
                    if storeMatrix:
                        colNum = obj.get_col_pos(col)                    
                    a = { 'fileID' : fileRecord.fileID, 'name' : col, 'axis' : 1, 'pos' : colNum }
                    self.sess.execute( table.insert(a) )
                    count += 1
                    if count % 1000 == 0:
                        self.sess.flush()
                
                if storeMatrix:
                    if obj.get_type() not in self.h5:
                        self.h5.create_group(obj.get_type())

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
                print "checking sum"             
                fileRecord.md5 = self.md5check(obj.path)
                print "check done"             
                self.sess.flush()


            self.sess.commit()
            
    
    def close(self):
        self.commit()
    
    def commit(self):
        pass
        #self.engine.commit()
