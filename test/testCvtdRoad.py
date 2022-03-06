import unittest

import inspect
import os
import sys
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

from cvtdNode import CvtdNode
from cvtdRoad import CvtdRoad
from cvtdRoadPoint import CvtdRoadPoint

class TestCvtdRoad(unittest.TestCase):
	def test_insert_increasing(self):
		road = CvtdRoad()
		road.points.append(CvtdRoadPoint(123, 85))
		road.points.append(CvtdRoadPoint(124, 120))
		road.points.append(CvtdRoadPoint(125, 160))

		road.insert(CvtdRoadPoint(1, 45))
		self.assertEqual(4, len(road.points))
		self.assertEqual(road.points[0].addr, 45)
		self.assertEqual(road.points[1].addr, 85)
		self.assertEqual(road.points[2].addr, 120)
		self.assertEqual(road.points[3].addr, 160)

		road.insert(CvtdRoadPoint(1, 145))
		self.assertEqual(5, len(road.points))
		self.assertEqual(road.points[0].addr, 45)
		self.assertEqual(road.points[1].addr, 85)
		self.assertEqual(road.points[2].addr, 120)
		self.assertEqual(road.points[3].addr, 145)
		self.assertEqual(road.points[4].addr, 160)

		road.insert(CvtdRoadPoint(1, 290))
		self.assertEqual(6, len(road.points))
		self.assertEqual(road.points[0].addr, 45)
		self.assertEqual(road.points[1].addr, 85)
		self.assertEqual(road.points[2].addr, 120)
		self.assertEqual(road.points[3].addr, 145)
		self.assertEqual(road.points[4].addr, 160)
		self.assertEqual(road.points[5].addr, 290)

	def test_insert_decreasing(self):
		road = CvtdRoad()
		road.points.append(CvtdRoadPoint(123, 160))
		road.points.append(CvtdRoadPoint(124, 120))
		road.points.append(CvtdRoadPoint(125, 85))

		road.insert(CvtdRoadPoint(1, 290))
		self.assertEqual(4, len(road.points))
		self.assertEqual(road.points[0].addr, 290)
		self.assertEqual(road.points[1].addr, 160)
		self.assertEqual(road.points[2].addr, 120)
		self.assertEqual(road.points[3].addr, 85)

		road.insert(CvtdRoadPoint(1, 145))
		self.assertEqual(5, len(road.points))
		self.assertEqual(road.points[0].addr, 290)
		self.assertEqual(road.points[1].addr, 160)
		self.assertEqual(road.points[2].addr, 145)
		self.assertEqual(road.points[3].addr, 120)
		self.assertEqual(road.points[4].addr, 85)

		road.insert(CvtdRoadPoint(1, 45))
		self.assertEqual(6, len(road.points))
		self.assertEqual(road.points[0].addr, 290)
		self.assertEqual(road.points[1].addr, 160)
		self.assertEqual(road.points[2].addr, 145)
		self.assertEqual(road.points[3].addr, 120)
		self.assertEqual(road.points[4].addr, 85)
		self.assertEqual(road.points[5].addr, 45)
	
	def test_compare_road(self):
		nodeDict = {}
		nodeDict[1] = CvtdNode(1, 1)
		nodeDict[2] = CvtdNode(2, 2)
		nodeDict[3] = CvtdNode(3, 3)
		nodeDict[4] = CvtdNode(4, 4)
		nodeDict[5] = CvtdNode(5, 5)
		nodeDict[6] = CvtdNode(6, 6)
		nodeDict[7] = CvtdNode(7, 7)
		nodeDict[8] = CvtdNode(8, 8)
		nodeDict[9] = CvtdNode(9, 9)

		road1 = CvtdRoad()
		road1.name = "Road A"
		road1.dir = "Up"
		road1.points.append(CvtdRoadPoint(1, 1))
		road1.points.append(CvtdRoadPoint(2, 2))
		road1.points.append(CvtdRoadPoint(3, 3))
		road1.points.append(CvtdRoadPoint(4, 4))
		road1.points.append(CvtdRoadPoint(5, 5))

		road2 = CvtdRoad()
		road2.name = "Road B"
		road2.dir = "Up"
		road2.points.append(CvtdRoadPoint(3, 3))
		road2.points.append(CvtdRoadPoint(4, 4))
		road2.points.append(CvtdRoadPoint(5, 5))
		road2.points.append(CvtdRoadPoint(6, 6))
		road2.points.append(CvtdRoadPoint(7, 7))

		road3 = CvtdRoad()
		road3.name = "Road C"
		road3.dir = "Up"
		road3.points.append(CvtdRoadPoint(4, 4))
		road3.points.append(CvtdRoadPoint(5, 5))
		road3.points.append(CvtdRoadPoint(6, 6))

		road4 = CvtdRoad()
		road4.name = "Road D"
		road4.dir = "Up"
		road4.points.append(CvtdRoadPoint(9, 9))
		road4.points.append(CvtdRoadPoint(8, 8))
		road4.points.append(CvtdRoadPoint(7, 7))

		road5 = CvtdRoad()
		road5.name = "Road E"
		road5.dir = "Up"
		road5.points.append(CvtdRoadPoint(4, 4))
		road5.points.append(CvtdRoadPoint(7, 7))

		import pdb; pdb.set_trace()
		self.assertEqual(0, road1.compare_road(nodeDict, road1, nodeDict))
		self.assertEqual(4, road1.compare_road(nodeDict, road2, nodeDict))
		self.assertEqual(4, road1.compare_road(nodeDict, road3, nodeDict))
		self.assertEqual(-1, road1.compare_road(nodeDict, road4, nodeDict))
		self.assertEqual(3, road1.compare_road(nodeDict, road5, nodeDict))

		self.assertEqual(4, road2.compare_road(nodeDict, road1, nodeDict))
		self.assertEqual(0, road2.compare_road(nodeDict, road2, nodeDict))
		self.assertEqual(1, road2.compare_road(nodeDict, road3, nodeDict))
		self.assertEqual(4, road2.compare_road(nodeDict, road4, nodeDict))
		self.assertEqual(3, road2.compare_road(nodeDict, road5, nodeDict))

		self.assertEqual(4, road3.compare_road(nodeDict, road1, nodeDict))
		self.assertEqual(2, road3.compare_road(nodeDict, road2, nodeDict))
		self.assertEqual(0, road3.compare_road(nodeDict, road3, nodeDict))
		self.assertEqual(-1, road3.compare_road(nodeDict, road4, nodeDict))
		self.assertEqual(4, road3.compare_road(nodeDict, road5, nodeDict))

		self.assertEqual(-1, road4.compare_road(nodeDict, road1, nodeDict))
		self.assertEqual(4, road4.compare_road(nodeDict, road2, nodeDict))
		self.assertEqual(-1, road4.compare_road(nodeDict, road3, nodeDict))
		self.assertEqual(0, road4.compare_road(nodeDict, road4, nodeDict))
		self.assertEqual(4, road4.compare_road(nodeDict, road5, nodeDict))

		self.assertEqual(3, road5.compare_road(nodeDict, road1, nodeDict))
		self.assertEqual(3, road5.compare_road(nodeDict, road2, nodeDict))
		self.assertEqual(4, road5.compare_road(nodeDict, road3, nodeDict))
		self.assertEqual(4, road5.compare_road(nodeDict, road4, nodeDict))
		self.assertEqual(0, road5.compare_road(nodeDict, road5, nodeDict))

if __name__ == '__main__':
	unittest.main()