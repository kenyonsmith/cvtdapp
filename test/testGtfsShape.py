import inspect
import os
import sys
import unittest

import datetime

from cvtdNode import CvtdNode

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

from gtfsShape import GtfsShape

class TestGtfsShape(unittest.TestCase):
    def test_compare_point_list(self):
        shape1 = GtfsShape()
        shape1.pointList.append(CvtdNode(1, 2))
        shape1.pointList.append(CvtdNode(2, 3))
        shape1.pointList.append(CvtdNode(3, 4))
        
        shape2 = GtfsShape()
        shape2.pointList.append(CvtdNode(2, 3))
        shape2.pointList.append(CvtdNode(3, 4))
        shape2.pointList.append(CvtdNode(1, 2))
        
        shape3 = GtfsShape()
        shape3.pointList.append(CvtdNode(1, 2))
        shape3.pointList.append(CvtdNode(1, 3))
        shape3.pointList.append(CvtdNode(2, 2))

        shape4 = GtfsShape()

        self.assertFalse(shape1.compare_point_list(shape2.pointList))
        self.assertTrue(shape1.compare_point_list(shape1.pointList))
        self.assertTrue(shape2.compare_point_list(shape2.pointList))
        self.assertFalse(shape2.compare_point_list(shape1.pointList))
        self.assertFalse(shape1.compare_point_list(shape3.pointList))
        self.assertFalse(shape2.compare_point_list(shape3.pointList))
        self.assertFalse(shape3.compare_point_list(shape2.pointList))
        self.assertFalse(shape3.compare_point_list(shape1.pointList))
        self.assertTrue(shape3.compare_point_list(shape3.pointList))
        
        self.assertFalse(shape4.compare_point_list(shape1.pointList))
        self.assertFalse(shape4.compare_point_list(shape2.pointList))
        self.assertFalse(shape4.compare_point_list(shape3.pointList))
        self.assertTrue(shape4.compare_point_list(shape4.pointList))

if __name__ == '__main__':
	unittest.main()