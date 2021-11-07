import unittest

import inspect
import os
import sys
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

from cvtdUtil import CvtdUtil

class TestCvtdUtil(unittest.TestCase):
	def test_coord_to_ft(self):
		self.assertEqual(CvtdUtil.coord_to_ft(1), 369600)
	
	def test_split_quotes(self):
		s = "1,2,3,'Once, upon a time, something happened',6"
		self.assertListEqual(["1", "2", "3", "'Once, upon a time, something happened'", "6"], CvtdUtil.split_quotes(s, ','))

		s2 = '"3,3","4,4","5,5"\n'
		self.assertListEqual(['"3,3"', '"4,4"', '"5,5"\n'], CvtdUtil.split_quotes(s2, ','))
	
	def test_split_double_quotes(self):
		s = "1,2,3,'Once, upon a time, something happened',6"
		self.assertListEqual(["1", "2", "3", "'Once", " upon a time", " something happened'", "6"], CvtdUtil.split_double_quotes(s, ','))

		s2 = '"3,3","4,4","5,5"\n'
		self.assertListEqual(['"3,3"', '"4,4"', '"5,5"\n'], CvtdUtil.split_double_quotes(s2, ','))
	
	def test_split_quotes_empty_field(self):
		s = "2,3,'boo',,\"hello\",,7"
		self.assertListEqual(["2", "3", "'boo'", "", "\"hello\"", "", "7"], CvtdUtil.split_quotes(s, ','))
	
	def test_parse_csv(self):
		with open('tmpTest1.csv', 'w') as f:
			f.write('a,b,c\n')
			f.write('5,,6\n')
			f.write('1,2,\n')
			f.write(',,\n')
			f.write('x,y,z\n')
			f.write('"3,3","4,4","5,5"\n')
		result = CvtdUtil.parse_csv('tmpTest1.csv')
		os.remove('tmpTest1.csv')
		self.assertListEqual(['5','1','','x','"3,3"'], result['a'])
		self.assertListEqual(['','2','','y','"4,4"'], result['b'])
		self.assertListEqual(['6','','','z','"5,5"'], result['c'])

if __name__ == '__main__':
	unittest.main()