import unittest
import subprocess
import shutil
import MySQLdb
import MySQLSandbox

class CGDataTestCase(unittest.TestCase):
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

        cmd = '../scripts/compileCancerData.py %s; cat out/* | mysql --defaults-file=%s hg18;' % (cls.datadir, cls.sandbox.defaults)
        f = open('test.log', 'a')
        p = subprocess.Popen(cmd, shell=True, stdout=f, stderr=f)
        p.communicate()
        f.close()
        if p.returncode != 0:
            raise subprocess.CalledProcessError(p.returncode, cmd)

    @classmethod
    def tearDownClass(cls):
        cls.sandbox.shutdown()
