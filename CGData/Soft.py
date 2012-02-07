
import sys
import re
import sqlite3

sectionLine = re.compile(r'^\^(\w*) = (\w*)')
metaLine = re.compile(r'^\!(\S*) = (.*)$')
columnDefLine = re.compile('^\#(.*) = (.*)$')

tableBegin = re.compile(r'^\!(\w*)_table_begin')
tableEnd = re.compile(r'^\!(\w*)_table_end')

colFix = re.compile(r'[_\ \-]')

def colNameFix(name):
    return colFix.sub("_", name)

class Soft:
    """
    This class is designed to read GPL soft files and dump them to an sqlite
    table
    """
    init_sql = [
        """CREATE TABLE section (
            id integer primary key not null,
            name string, 
            type string
        )""",
        """CREATE TABLE attributes (
            section integer not null,
            name string,
            value text
        )""",
        """CREATE TABLE columns (
            section integer not null,
            tablename string,
            name string,
            colname string,
            definition text
        )        
        """
    ]
    
    init_datatable = """CREATE TABLE data_%s (
        %s
    )    
    """
    
    def __init__(self, dbfile):
        self.dbfile = dbfile
        self._cursor = None
        self._conn = None
        self._section_ids = {}

    def _open(self):
        if self._conn is None:
            self._conn = sqlite3.connect(self.dbfile)        
            self._cursor = self._conn.cursor()
        
    
    def _add_section(self, name, sectionType):
        self._cursor.execute("insert into section(name, type) values(?,?)", [name,sectionType])
        self._conn.commit()
    
    def _get_sectionid(self, section):
        sid = None
        if section not in self._section_ids:
            self._cursor.execute("select id from section where name = ?", [section])
            sid = self._cursor.fetchone()[0]
            self._section_ids[section] = sid
        else:
            sid = self._section_ids[section]        
        return sid
        
    def _add_attribute(self, section, name, value):
        sid = self._get_sectionid(section)
        self._cursor.execute("insert into attributes(section, name, value) values(?,?,?)", [sid, name.decode('utf-8', 'ignore'), value.decode('utf-8', 'ignore')])

    def _add_column(self, section, col, colname, definition):
        sid = self._get_sectionid(section)
        self._cursor.execute("insert into columns(section, tablename, name, colname, definition) values(?,?,?,?,?)", [sid, "data_" + section, col, colname, definition])
        self._conn.commit()
    
    def _create_datatable(self, name, cols):
        coldef = []
        for col in cols:
            coldef.append("\t%s string" % (col))
        self._cursor.execute( self.init_datatable % (name, ",".join(coldef)) )
    
    def _add_data(self, table, vals):
        k = vals.keys()
        v = []
        for c in k:
            v.append(vals[c])
        insert = "INSERT into %s(%s) values(%s)" % (table, ",".join(k), ",".join(["?"] * len(v)) )
        self._cursor.execute(insert, v)
    
    def read(self, handle):

        self._open()
        
        for sql in self.init_sql:
            self._cursor.execute(sql)
        
        inTable = False
        section_name = None
        col_pos = 0
        cols={}
        head = None
        for line in handle:
            found = False
            res = sectionLine.search(line)
            if res:
                found = True
                section_name = res.group(2)
                self._add_section(section_name, res.group(1))
                col_pos = 0
                cols = {}
                head = None
            
            res = metaLine.search(line)
            if res:
                found = True
                self._add_attribute(section_name, res.group(1), res.group(2))
            
            res = columnDefLine.search(line)
            if res:
                cname = colNameFix(res.group(1))
                cols[res.group(1)] = cname
                self._add_column(section_name, res.group(1), cname, res.group(2))
                col_pos += 1
                found = True

            res = tableBegin.search(line)
            if res:
                found = True
                inTable = True
                
            res = tableEnd.search(line)
            if res:
                found = True
                inTable = False

            if not found and inTable:
                found = True
                if head is None:
                    tmp = line.rstrip().split("\t")
                    head = []
                    for c in tmp:
                        head.append(cols[c])
                    self._create_datatable(section_name, head)
                else:
                    tmp = line.rstrip().split("\t")
                    vals = {}
                    for i, c in enumerate(head):
                        if i < len(tmp):                           
                            vals[c] = tmp[i]
                    self._add_data("data_" + section_name, vals)
            
            if not found:
                sys.stdout.write(line)
        self._conn.commit()
    
    def get_section_list(self, name="%"):
        self._open()
        self._cursor.execute("select name from section where type like ?", [name])
        for row in self._cursor.fetchall():
            yield row[0]
    
    def get_meta(self, section):
        out = {}
        self._open()
        sid = self._get_sectionid(section)
        self._cursor.execute("SELECT name, value from attributes WHERE section = ?", [sid])
        for row in self._cursor.fetchall():
            if row[0] not in out:
                out[row[0]] = []
            out[row[0]].append(row[1])
        for col in out:
            if len(out[col]) == 1:
                out[col] = out[col][0]
        return out
    
    def get_col_list(self,section):
        self._open()
        sid = self._get_sectionid(section)
        self._cursor.execute("SELECT name from columns WHERE section = ?", [sid])
        for row in self._cursor.fetchall():
            yield row[0]
        
