import unittest
import os

import subprocess
import shutil
import MySQLdb
import MySQLSandbox

class TestCase(unittest.TestCase):
    """Test sample ordering in output tables"""
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

CREATE TABLE raDb (
    name varchar(255),  # Table name for genomic data
    downSampleTable varchar(255),       # Down-sampled table
    sampleTable varchar(255),   # Sample table
    clinicalTable varchar(255), # Clinical table
    columnTable varchar(255),   # Column table
    shortLabel varchar(255),    # Short label
    longLabel varchar(255),     # Long label
    expCount int unsigned,      # Number of samples
    groupName varchar(255),     # Group name
    microscope varchar(255),    # hgMicroscope on/off flag
    aliasTable varchar(255),    # Probe to gene mapping
    dataType varchar(255),      # data type (bed 15)
    platform varchar(255),      # Expression, SNP, etc.
    security varchar(255),      # Security setting (public, private)
    profile varchar(255),       # Database profile
    PRIMARY KEY(name)
);""")
        while cls.c.nextset() is not None: pass

        cmd = '../scripts/compileCancerData.py data_sample_order; cat out/* | mysql --defaults-file=%s hg18;' % cls.sandbox.defaults
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, errors = p.communicate()
        if p.returncode != 0:
            raise subprocess.CalledProcessError(p.returncode, cmd)

    @classmethod
    def tearDownClass(cls):
        cls.sandbox.shutdown()

    def test_sample(self):
        self.c.execute("""select id, sampleName from sample_test order by id""")
        rows = self.c.fetchall()
        self.assertEqual(len(rows), 5)          # one sample
        self.assertEqual(rows[0][0], 0)         # sample id is zero
        self.assertEqual(rows[0][1], 'sample1') # sample name is sample1

        self.assertEqual(rows[1][0], 1)
        self.assertEqual(rows[1][1], 'sample4')

        self.assertEqual(rows[2][0], 2)
        self.assertEqual(rows[2][1], 'sample17')

        self.assertEqual(rows[3][0], 3)
        self.assertEqual(rows[3][1], 'sample63')

        self.assertEqual(rows[4][0], 4)
        self.assertEqual(rows[4][1], 'sample101')

    def test_clinical(self):
        """Test sample order in the clinical table"""
        self.c.execute("""select sampleName from clinical_test order by sampleName""")
        rows = self.c.fetchall()
        self.assertEqual(len(rows), 5)          # five samples
        self.assertEqual(rows[0][0], 'sample1') # sample name is sample1
        self.assertEqual(rows[1][0], 'sample4')
        self.assertEqual(rows[2][0], 'sample17')
        self.assertEqual(rows[3][0], 'sample63')
        self.assertEqual(rows[4][0], 'sample101')

    def test_genomic(self):
        """Test sample order in the genomic table"""
        self.c.execute("""select expIds,expScores from genomic_test""")
        rows = self.c.fetchall()
        self.assertEqual(len(rows), 1)                          # one probe
        self.assertEqual(rows[0][0], '0,1,2,3,4')               # ordered by sample id
        values = map(lambda x: float(x), rows[0][1].split(',')) # scores are in correct order
        self.assertTrue(values[0] - 0.479005065149792 < self.tolerance)
        self.assertTrue(values[1] - 25.1 < self.tolerance)
        self.assertTrue(values[2] - 5.3 < self.tolerance)
        self.assertTrue(values[3] - 3.1 < self.tolerance)
        self.assertTrue(values[4] - -1.23 < self.tolerance)

def main():
    sys.argv = sys.argv[:1]
    unittest.main()

if __name__ == '__main__':
    main()
