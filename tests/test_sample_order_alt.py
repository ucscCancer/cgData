import unittest
from utils import CGDataTestCase

class TestCase(CGDataTestCase):
    """Test sample ordering in output tables"""

    datadir = 'data_sample_order_alt2'

    def test_sample(self):
        self.c.execute("""select id, sampleName from sample_test order by id""")
        rows = self.c.fetchall()
        self.assertEqual(len(rows), 5)          # one sample
        self.assertEqual(rows[0][0], 0)         # sample id is zero
        self.assertEqual(rows[0][1], '1') # sample name is 1

        self.assertEqual(rows[1][0], 1)
        self.assertEqual(rows[1][1], '101')

        self.assertEqual(rows[2][0], 2)
        self.assertEqual(rows[2][1], '17')

        self.assertEqual(rows[3][0], 3)
        self.assertEqual(rows[3][1], '4')

        self.assertEqual(rows[4][0], 4)
        self.assertEqual(rows[4][1], 'sample63')


    def test_clinical(self):
        """Test sample order in the clinical table"""
        self.c.execute("""select codes.value from codes, clinical_test where codes.id = clinical_test.sampleName order by codes.ordering""")
        rows = self.c.fetchall()
        self.assertEqual(len(rows), 5)          # five samples
        self.assertEqual(rows[0][0], '1') # sample name is sample1
        self.assertEqual(rows[1][0], '101')
        self.assertEqual(rows[2][0], '17')
        self.assertEqual(rows[3][0], '4')
        self.assertEqual(rows[4][0], 'sample63')

    def test_genomic(self):
        """Test sample order in the genomic table"""
        self.c.execute("""select expIds,expScores from genomic_test""")
        rows = self.c.fetchall()
        self.assertEqual(len(rows), 1)                          # one probe
        self.assertEqual(rows[0][0], '0,1,2,3,4')               # ordered by sample id
        values = map(lambda x: float(x), rows[0][1].split(',')) # scores are in correct order
        self.assertTrue(values[0] - 0.479005065149792 < self.tolerance)
        self.assertTrue(values[1] - -1.23 < self.tolerance)
        self.assertTrue(values[2] - 5.3 < self.tolerance)
        self.assertTrue(values[3] - 25.1 < self.tolerance)
        self.assertTrue(values[4] - 3.1 < self.tolerance)

def main():
    sys.argv = sys.argv[:1]
    unittest.main()

if __name__ == '__main__':
    main()
