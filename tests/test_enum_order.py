import unittest
from utils import CGDataTestCase


class TestCase(CGDataTestCase):
    """Test feature ordering in output tables"""
    datadir = "data_enum_order2"

    def test_clinical(self):
        """Test enum order in the clinical table"""
        self.c.execute("""SELECT c1.value, c2.value FROM codes AS c1, clinical_test"""
                + """ LEFT JOIN codes AS c2 ON `color` = c2.id"""
                + """ WHERE c1.id = clinical_test.sampleName ORDER BY c2.ordering;""")
        rows = self.c.fetchall()
        self.assertEqual(len(rows), 6)          # six samples
        self.assertEqual(rows[0][0], 'sample4') # sample name is sample4
        self.assertEqual(rows[1][0], 'sample1')
        self.assertEqual(rows[2][0], 'sample3')
        self.assertEqual(rows[3][0], 'sample2')
        self.assertEqual(rows[4][0], 'sample6')
        self.assertEqual(rows[5][0], 'sample5')

def main():
    sys.argv = sys.argv[:1]
    unittest.main()

if __name__ == '__main__':
    main()
