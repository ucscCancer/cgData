import unittest
from utils import CGDataTestCase

class TestCase(CGDataTestCase):
    """Test coded feature with numeric states"""
    datadir = 'data_numeric_enum'

    def test_clinical(self):
        """Test enum order in the clinical table"""
        self.c.execute("""SELECT c1.value, c2.value FROM codes AS c1, clinical_test"""
                + """ LEFT JOIN codes AS c2 ON `HER2+` = c2.id"""
                + """ WHERE c1.id = clinical_test.sampleName ORDER BY c2.ordering,c1.ordering;""")
        rows = self.c.fetchall()
        self.assertEqual(len(rows), 6)          # six samples
        self.assertEqual(rows[0], ( 'sample1', '0' ) ) # sample name is sample1
        self.assertEqual(rows[1], ( 'sample2', '0' ) )
        self.assertEqual(rows[2], ( 'sample4', '0' ) )
        self.assertEqual(rows[3], ( 'sample3', '1' ) )
        self.assertEqual(rows[4], ( 'sample5', '1' ) )
        self.assertEqual(rows[5], ( 'sample6', '1' ) )

def main():
    sys.argv = sys.argv[:1]
    unittest.main()

if __name__ == '__main__':
    main()
