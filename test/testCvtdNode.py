import unittest

import inspect
import os
import sys
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

from cvtdNode import CvtdNode

class TestCvtdNode(unittest.TestCase):
	def test_compare_node(self):
		node = CvtdNode(41.1366832, -111.8196642)
		self.assertTrue(node.compare_node(node))
		self.assertTrue(node.compare_node(CvtdNode(41.1366833, -111.8196646)))
		self.assertTrue(node.compare_node(CvtdNode(41.1366827, -111.8196634)))
		self.assertFalse(node.compare_node(CvtdNode(41.1366827, -111.8197634)))
		self.assertFalse(node.compare_node(CvtdNode(41.1367827, -111.8196634)))
		self.assertFalse(node.compare_node(CvtdNode(41.1367827, -111.8197634)))

if __name__ == '__main__':
	unittest.main()