import unittest
from utils import CGDataTestCase

class TestCase(CGDataTestCase):
    """Test feature ordering in output tables"""
    datadir = 'data_enum_order_quote'

    def test_clinical(self):
        """Test enum order in the clinical table"""
        self.c.execute("""select sampleName, color from clinical_test order by color,sampleName""")
        rows = self.c.fetchall()
        self.assertEqual(len(rows), 6)          # six samples
        self.assertEqual(rows[0][0], 'sample4') # sample name is sample4
        self.assertEqual(rows[0][1], 'Red')
        self.assertEqual(rows[1][0], 'sample1')
        self.assertEqual(rows[1][1], 'Red,Yellow')
        self.assertEqual(rows[2][0], 'sample3')
        self.assertEqual(rows[2][1], 'Blue,Yellow')
        self.assertEqual(rows[3][0], 'sample2')
        self.assertEqual(rows[3][1], 'Blue')
        self.assertEqual(rows[4][0], 'sample6')
        self.assertEqual(rows[4][1], 'Blue')
        self.assertEqual(rows[5][0], 'sample5')
        self.assertEqual(rows[5][1], 'Red,Blue')

def main():
    sys.argv = sys.argv[:1]
    unittest.main()

if __name__ == '__main__':
    main()
