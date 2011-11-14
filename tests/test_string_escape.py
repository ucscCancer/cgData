import unittest
from utils import CGDataTestCase

class TestCase(CGDataTestCase):
    '''Test string escapes on odd input characters'''
    datadir = 'data_string_escape'

    def test_sample(self):
        self.c.execute("""select id, sampleName from sample_test""")
        rows = self.c.fetchall()
        self.assertEqual(len(rows), 1)          # one sample
        self.assertEqual(rows[0][0], 0)         # sample id is zero
        self.assertEqual(rows[0][1], 'sample1"\'`\\') # sample name is sample1"'`\

    def test_sample_column_order(self):
        self.c.execute("""select * from sample_test""")
        rows = self.c.fetchall()
        self.assertEqual([d[0] for d in self.c.description],
                ['id', 'sampleName'])

    def test_alias(self):
        self.c.execute("""select name, alias from genomic_test_alias""")
        rows = self.c.fetchall()
        self.assertEqual(len(rows), 1)          # one probe
        self.assertEqual(rows[0][0], 'probe1"\'`\\')  # probe name
        self.assertEqual(rows[0][1], 'geneA"\'`\\')   # alias name

    def test_alias_column_order(self):
        self.c.execute("""select * from genomic_test_alias""")
        rows = self.c.fetchall()
        self.assertEqual([d[0] for d in self.c.description],
                ['name', 'alias'])

    def test_colDb(self):
        self.c.execute("""select name, shortLabel, longLabel, valField, clinicalTable, priority, filterType, visibility, groupName from colDb""")
        rows = self.c.fetchall()
        self.assertEqual(len(rows), 3)                  # three features (sampleName plus two in the matrix)
        self.assertEqual(rows[0][0], 'age"\'__')             # name
        self.assertEqual(rows[0][1], 'age"\'__')             # short
        self.assertEqual(rows[0][2], 'age"\'__')             # long
        self.assertEqual(rows[0][3], 'age"\'__')             # field
        self.assertEqual(rows[0][4], 'clinical_test')   # table
        self.assertEqual(rows[0][5], 1)                 # priority
        self.assertEqual(rows[0][6], 'minMax')          # filterType
        self.assertEqual(rows[0][7], 'on')              # visibility
        self.assertEqual(rows[0][8], None)              # groupName

        self.assertEqual(rows[1][0], 'status')          # name
        self.assertEqual(rows[1][1], 'status')          # short
        self.assertEqual(rows[1][2], 'status')          # long
        self.assertEqual(rows[1][3], 'status')          # field
        self.assertEqual(rows[1][4], 'clinical_test')   # table
        self.assertEqual(rows[1][5], 1)                 # priority
        self.assertEqual(rows[1][6], 'coded')           # filterType
        self.assertEqual(rows[1][7], 'on')              # visibility
        self.assertEqual(rows[1][8], None)              # groupName

        self.assertEqual(rows[2][0], 'sampleName')      # name
        self.assertEqual(rows[2][1], 'Sample name')     # short
        self.assertEqual(rows[2][2], 'Sample name')     # long
        self.assertEqual(rows[2][3], 'sampleName')      # field
        self.assertEqual(rows[2][4], 'clinical_test')   # table
        self.assertEqual(rows[2][5], 1)                 # priority
        self.assertEqual(rows[2][6], 'coded')           # filterType
        self.assertEqual(rows[2][7], 'on')              # visibility
        self.assertEqual(rows[2][8], None)              # groupName

    def test_clinical(self):
        self.c.execute("""SELECT sampleID, c1.value, `age"'__`, c2.value FROM codes AS c1, clinical_test"""
                + """ LEFT JOIN codes AS c2 ON `status` = c2.id"""
                + """ WHERE c1.id = clinical_test.sampleName;""")
        rows = self.c.fetchall()
        self.assertEqual(len(rows), 1)          # one sample x one probe
        self.assertEqual(rows[0][0], 0)         # id
        self.assertEqual(rows[0][1], 'sample1"\'`\\') # name
        self.assertEqual(rows[0][2], 3)         # age
        self.assertEqual(rows[0][3], 'Negative"\'`\\')# status

    def test_genomic(self):
        self.c.execute("""select chrom,chromStart,chromEnd,name,expCount,expIds,expScores from genomic_test""")
        rows = self.c.fetchall()
        self.assertEqual(len(rows), 1)          # one sample x one probe
        self.assertEqual(rows[0][0], 'chrX')    # chrom
        self.assertEqual(rows[0][1], 1)         # start
        self.assertEqual(rows[0][2], 10)        # end
        self.assertEqual(rows[0][3], 'probe1"\'`\\')  # name
        self.assertEqual(rows[0][4], 1)         # count
        self.assertEqual(rows[0][5], '0')       # expIds
        self.assertTrue(float(rows[0][6]) - 0.479005065149792 < self.tolerance)  # expScores

    def test_genomic_order(self):
        self.c.execute("""select * from genomic_test""")
        rows = self.c.fetchall()
        # this is bed15
        self.assertEqual([d[0] for d in self.c.description],
            ['id', 'chrom', 'chromStart', 'chromEnd', 'name', 'score', 'strand', 'thickStart',
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
        self.assertEqual(rows[0][5], 'test1"\'`\\')             # short
        self.assertEqual(rows[0][6], 'test One"\'`\\')                # long
        self.assertEqual(rows[0][7], 1)                         # count
        self.assertEqual(rows[0][8], 'test1 group')             # group
        self.assertEqual(rows[0][9], None)                      # microscope
        self.assertEqual(rows[0][10], 'genomic_test_alias')     # alias
        self.assertEqual(rows[0][11], 'bed 15')                 # datatype
        self.assertEqual(rows[0][12], 'expression')             # platform
        self.assertEqual(rows[0][13], 'public')                 # security
        self.assertEqual(rows[0][14], 'localDb')                # profile
        self.assertEqual(rows[0][15], 'wrangler"\'`\\')         # wrangler
        self.assertEqual(rows[0][16], 'http://url.com"\'`\\')   # url
        self.assertEqual(rows[0][17], 'test1 article title"\'`\\')    # article_title
        self.assertEqual(rows[0][18], 'track cite"\'`\\')             # citation
        self.assertEqual(rows[0][19], 'author1,author2"\'`\\')  # author_list
        self.assertEqual(rows[0][20], 'wrangling procedure"\'`\\')    # wrangling_procedure

def main():
    sys.argv = sys.argv[:1]
    unittest.main()

if __name__ == '__main__':
    main()
