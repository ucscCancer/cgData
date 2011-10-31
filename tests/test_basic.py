#!/usr/bin/env python

import unittest
import os

import subprocess
import shutil
import MySQLdb
import MySQLSandbox

class TestCase(unittest.TestCase):
    tolerance = 0.001 # floating point tolerance

    @classmethod
    def setUpClass(cls):
        try:
            shutil.rmtree('out')
        except:
            pass
        cls.sandbox = MySQLSandbox.Sandbox()
        db = MySQLdb.connect(read_default_file=cls.sandbox.defaults)
        cls.c = db.cursor()
        # create raDb and hg18
        cls.c.execute("""
create database hg18;
use hg18;

CREATE TABLE colDb (
    `id` int(10) unsigned NOT NULL PRIMARY KEY AUTO_INCREMENT,
    name varchar(255),	# Column name
    shortLabel varchar(255),	# Short label
    longLabel varchar(255),	# Long label
    valField varchar(255),	# Val field name
    clinicalTable varchar(255),	# Table of clinical data
    priority float,	# Priority
    filterType varchar(255),	# Filter Type - minMax or coded
    visibility varchar(255),	# Visibility
    groupName varchar(255)	# Group Name
) engine 'MyISAM';

CREATE TABLE raDb (
    name varchar(255),	# Table name for genomic data
    downSampleTable varchar(255),	# Down-sampled table
    sampleTable varchar(255),	# Sample table
    clinicalTable varchar(255),	# Clinical table
    columnTable varchar(255),	# Column table
    shortLabel varchar(255),	# Short label
    longLabel varchar(255),	# Long label
    expCount int unsigned,	# Number of samples
    groupName varchar(255),	# Group name
    microscope varchar(255),	# hgMicroscope on/off flag
    aliasTable varchar(255),	# Probe to gene mapping
    dataType varchar(255),	# data type (bed 15)
    platform varchar(255),	# Expression, SNP, etc.
    security varchar(255),	# Security setting (public, private)
    profile varchar(255),	# Database profile
    gain float,	# Gain
    priority float,	# Priority for sorting
    url varchar(255),	# Pubmed URL
    wrangler varchar(255),	# Wrangler
    citation varchar(255),	# Citation
    article_title longblob,	# Title of publication
    author_list longblob,	# Author list
    wrangling_procedure longblob,	# Wrangling
              #Indices
    PRIMARY KEY(name)
);
""")
        while cls.c.nextset() is not None: pass

        cmd = '../scripts/compileCancerData.py data_basic; cat out/* | mysql --defaults-file=%s hg18;' % cls.sandbox.defaults
        f = open('test.log', 'a')
        p = subprocess.Popen(cmd, shell=True, stdout=f, stderr=f)
        p.communicate()
        f.close()
        if p.returncode != 0:
            raise subprocess.CalledProcessError(p.returncode, cmd)

    @classmethod
    def tearDownClass(cls):
        cls.sandbox.shutdown()

    def test_sample(self):
        self.c.execute("""select id, sampleName from sample_test""")
        rows = self.c.fetchall()
        self.assertEqual(len(rows), 1)          # one sample
        self.assertEqual(rows[0][0], 0)         # sample id is zero
        self.assertEqual(rows[0][1], 'sample1') # sample name is sample1

    def test_sample_column_order(self):
        self.c.execute("""select * from sample_test""")
        rows = self.c.fetchall()
        self.assertEqual([d[0] for d in self.c.description],
                ['id', 'sampleName'])

    def test_alias(self):
        self.c.execute("""select name, alias from genomic_test_alias""")
        rows = self.c.fetchall()
        self.assertEqual(len(rows), 1)          # one probe
        self.assertEqual(rows[0][0], 'probe1')  # probe name
        self.assertEqual(rows[0][1], 'geneA')   # alias name

    def test_alias_column_order(self):
        self.c.execute("""select * from genomic_test_alias""")
        rows = self.c.fetchall()
        self.assertEqual([d[0] for d in self.c.description],
                ['name', 'alias'])

    def test_colDb(self):
        self.c.execute("""select name, shortLabel, longLabel, valField, clinicalTable, priority, filterType, visibility, groupName from colDb""")
        rows = self.c.fetchall()
        self.assertEqual(len(rows), 3)                  # three features (sampleName plus two in the matrix)
        self.assertEqual(rows[0][0], 'sampleName')      # name
        self.assertEqual(rows[0][1], 'sample name')     # short
        self.assertEqual(rows[0][2], 'sample name')     # long
        self.assertEqual(rows[0][3], 'sampleName')      # field
        self.assertEqual(rows[0][4], 'clinical_test')   # table
        self.assertEqual(rows[0][5], 1)                 # priority
        self.assertEqual(rows[0][6], 'coded')           # filterType
        self.assertEqual(rows[0][7], 'on')              # visibility
        self.assertEqual(rows[0][8], None)              # groupName

        self.assertEqual(rows[1][0], 'age')             # name
        self.assertEqual(rows[1][1], 'age')             # short
        self.assertEqual(rows[1][2], 'age')             # long
        self.assertEqual(rows[1][3], 'age')             # field
        self.assertEqual(rows[1][4], 'clinical_test')   # table
        self.assertEqual(rows[1][5], 1)                 # priority
        self.assertEqual(rows[1][6], 'minMax')          # filterType
        self.assertEqual(rows[1][7], 'on')              # visibility
        self.assertEqual(rows[1][8], None)              # groupName

        self.assertEqual(rows[2][0], 'status')          # name
        self.assertEqual(rows[2][1], 'status')          # short
        self.assertEqual(rows[2][2], 'status')          # long
        self.assertEqual(rows[2][3], 'status')          # field
        self.assertEqual(rows[2][4], 'clinical_test')   # table
        self.assertEqual(rows[2][5], 1)                 # priority
        self.assertEqual(rows[2][6], 'coded')           # filterType
        self.assertEqual(rows[2][7], 'on')              # visibility
        self.assertEqual(rows[2][8], None)              # groupName

    def test_clinical(self):
        self.c.execute("""select sampleID,sampleName,age,status from clinical_test""")
        rows = self.c.fetchall()
        self.assertEqual(len(rows), 1)          # one sample x one probe
        self.assertEqual(rows[0][0], 0)         # id
        self.assertEqual(rows[0][1], 'sample1') # name
        self.assertEqual(rows[0][2], 3)         # age
        self.assertEqual(rows[0][3], 'Negative')# status

    def test_genomic(self):
        self.c.execute("""select chrom,chromStart,chromEnd,name,expCount,expIds,expScores from genomic_test""")
        rows = self.c.fetchall()
        self.assertEqual(len(rows), 1)          # one sample x one probe
        self.assertEqual(rows[0][0], 'chrX')    # chrom
        self.assertEqual(rows[0][1], 1)         # start
        self.assertEqual(rows[0][2], 10)        # end
        self.assertEqual(rows[0][3], 'probe1')  # name
        self.assertEqual(rows[0][4], 1)         # count
        self.assertEqual(rows[0][5], '0')       # expIds
        self.assertTrue(float(rows[0][6]) - 0.479005065149792 < self.tolerance)  # expScores

    def test_genomic_order(self):
        self.c.execute("""select * from genomic_test""")
        rows = self.c.fetchall()
        # this is bed15
        self.assertEqual([d[0] for d in self.c.description],
            ['bin', 'chrom', 'chromStart', 'chromEnd', 'name', 'score', 'strand', 'thickStart',
                'thickEnd', 'reserved', 'blockCount', 'blockSizes', 'chromStarts', 'expCount', 'expIds', 'expScores'])

    def test_raDb(self):
        self.c.execute("""select name,downSampleTable,sampleTable,clinicalTable,columnTable,shortLabel,longLabel,expCount,groupName,microscope,aliasTable,dataType,platform,security,profile,wrangler,url,article_title,citation,author_list,wrangling_procedure from raDb""")
        rows = self.c.fetchall()
        self.assertEqual(len(rows), 1)                          # one track
        self.assertEqual(rows[0][0], 'genomic_test')            # name
        self.assertEqual(rows[0][1], None)                      # downSampleTable
        self.assertEqual(rows[0][2], 'sample_test')             # sampleTable
        self.assertEqual(rows[0][3], 'clinical_test')           # clinical
        self.assertEqual(rows[0][4], 'colDb')                   # colDb
        self.assertEqual(rows[0][5], 'test1')                   # short
        self.assertEqual(rows[0][6], 'test One')                # long
        self.assertEqual(rows[0][7], 1)                         # count
        self.assertEqual(rows[0][8], 'test1 group')             # group
        self.assertEqual(rows[0][9], None)                      # microscope
        self.assertEqual(rows[0][10], 'genomic_test_alias')     # alias
        self.assertEqual(rows[0][11], 'bed 15')                 # datatype
        self.assertEqual(rows[0][12], 'expression')             # platform
        self.assertEqual(rows[0][13], 'public')                 # security
        self.assertEqual(rows[0][14], 'localDb')                # profile
        self.assertEqual(rows[0][15], 'wrangler')               # wrangler
        self.assertEqual(rows[0][16], 'http://url.com')         # url
        self.assertEqual(rows[0][17], 'test1 article title')    # article_title
        self.assertEqual(rows[0][18], 'track cite')             # citation
        self.assertEqual(rows[0][19], 'author1,author2')        # author_list
        self.assertEqual(rows[0][20], 'wrangling procedure')    # wrangling_procedure

def main():
    sys.argv = sys.argv[:1]
    unittest.main()

if __name__ == '__main__':
    main()
