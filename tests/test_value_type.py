import unittest
from utils import CGDataTestCase

class TestCase(CGDataTestCase):
    """Test feature value type setting"""
    datadir = 'data_value_type'

    def test_clinical(self):
        """Test value type in the clinical feature"""
        self.c.execute("""SELECT c1.value, age, c2.value FROM codes AS c1, clinical_test"""
                + """ LEFT JOIN codes AS c2 ON `color` = c2.id"""
                + """ WHERE c1.id = clinical_test.sampleName ORDER BY c2.ordering,c1.ordering;""")
        rows = self.c.fetchall()
        self.assertEqual(len(rows), 6)          # six samples
        self.assertEqual(rows[0][0], 'sample4') # sample name is sample4
        self.assertEqual(rows[0][1], 4.04) # sample name is sample4
        self.assertEqual(rows[1][0], 'sample1')
        self.assertEqual(rows[1][1], 1.01)
        self.assertEqual(rows[2][0], 'sample3')
        self.assertEqual(rows[2][1], 3.03)
        self.assertEqual(rows[3][0], 'sample2')
        self.assertEqual(rows[3][1], 2.02)
        self.assertEqual(rows[4][0], 'sample6')
        self.assertEqual(rows[4][1], 6.06)
        self.assertEqual(rows[5][0], 'sample5')
        self.assertEqual(rows[5][1], 5.05)

def main():
    sys.argv = sys.argv[:1]
    unittest.main()

if __name__ == '__main__':
    main()
