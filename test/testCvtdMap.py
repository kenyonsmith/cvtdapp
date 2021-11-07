import unittest

import inspect
import os
import sys
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

from cvtdContainedRoadPoint import ContainedRoadPoint
from cvtdBus import CvtdBus
from cvtdMap import CvtdMap
from cvtdNode import CvtdNode
from cvtdRoad import CvtdRoad
from cvtdRoadPoint import CvtdRoadPoint
from cvtdRoute import CvtdRoute
from cvtdRouteSegment import CvtdRouteSegment
from cvtdRouteStop import CvtdRouteStop

class TestCvtdMap(unittest.TestCase):
	def test_find_intersecting_roads(self):
		myMap = CvtdMap()
		myMap.nodeList.append(CvtdNode(1, 1))
		myMap.nodeList.append(CvtdNode(4, 4))
		myMap.nodeList.append(CvtdNode(1, 4))
		myMap.nodeList.append(CvtdNode(4, 1))
		myMap.nodeList.append(CvtdNode(3, 4))
		myMap.nodeList.append(CvtdNode(4, 3))
		
		thisRoad = CvtdRoad()
		thisRoad.name = "Road from 1,1 to 4,4"
		thisRoad.dir = "Up"
		thisRoad.points.append(CvtdRoadPoint(0, 0))
		thisRoad.points.append(CvtdRoadPoint(1, 60))
		myMap.roadList.append(thisRoad)
		
		thisRoad = CvtdRoad()
		thisRoad.name = "Road from 1,4 to 4,1"
		thisRoad.dir = "Up"
		thisRoad.points.append(CvtdRoadPoint(2, 0))
		thisRoad.points.append(CvtdRoadPoint(3, 60))
		myMap.roadList.append(thisRoad)
		
		thisRoad = CvtdRoad()
		thisRoad.name = "Road from 3,4 to 4,3"
		thisRoad.dir = "Up"
		thisRoad.points.append(CvtdRoadPoint(4, 0))
		thisRoad.points.append(CvtdRoadPoint(5, 50))
		myMap.roadList.append(thisRoad)
		
		intersections = myMap.find_intersecting_roads(0, 0)
		self.assertEqual(2, len(intersections))
		self.assertEqual(0, intersections[0][0].roadIx)
		self.assertEqual(30, intersections[0][0].addr)
		self.assertEqual(1, intersections[0][1].roadIx)
		self.assertEqual(30, intersections[0][1].addr)
		self.assertEqual(0, intersections[1][0].roadIx)
		self.assertEqual(50, intersections[1][0].addr)
		self.assertEqual(2, intersections[1][1].roadIx)
		self.assertEqual(25, intersections[1][1].addr)

	def test_nonintersecting_roads(self):
		myMap = CvtdMap()
		myMap.nodeList.append(CvtdNode(1, 1))
		myMap.nodeList.append(CvtdNode(2, 1))
		myMap.nodeList.append(CvtdNode(1, 4))
		myMap.nodeList.append(CvtdNode(2, 6))
		myMap.nodeList.append(CvtdNode(2, 9))
		myMap.nodeList.append(CvtdNode(3, 3))
		myMap.nodeList.append(CvtdNode(4, 6))
		
		thisRoad = CvtdRoad()
		thisRoad.name = "Road from 1,1 to 2,9"
		thisRoad.dir = "Up"
		thisRoad.points.append(CvtdRoadPoint(0, 0))
		thisRoad.points.append(CvtdRoadPoint(2, 60))
		thisRoad.points.append(CvtdRoadPoint(3, 90))
		thisRoad.points.append(CvtdRoadPoint(4, 100))
		myMap.roadList.append(thisRoad)
		
		thisRoad = CvtdRoad()
		thisRoad.name = "Road from 2,1 to 4,6"
		thisRoad.dir = "Up"
		thisRoad.points.append(CvtdRoadPoint(1, 0))
		thisRoad.points.append(CvtdRoadPoint(5, 60))
		thisRoad.points.append(CvtdRoadPoint(6, 100))
		myMap.roadList.append(thisRoad)
		
		intersections = myMap.find_intersecting_roads(0, 0)
		self.assertEqual(0, len(intersections))

	def test_multipoint_intersecting_roads(self):
		myMap = CvtdMap()
		myMap.nodeList.append(CvtdNode(1, 1))
		myMap.nodeList.append(CvtdNode(1, 3))
		myMap.nodeList.append(CvtdNode(1, 5))
		myMap.nodeList.append(CvtdNode(3, 1))
		myMap.nodeList.append(CvtdNode(3, 3))
		myMap.nodeList.append(CvtdNode(3, 5))
		
		myMap.nodeList.append(CvtdNode(2, 2))
		myMap.nodeList.append(CvtdNode(2, 4))
		myMap.nodeList.append(CvtdNode(4, 4))
		myMap.nodeList.append(CvtdNode(4, 2))
		
		thisRoad = CvtdRoad()
		thisRoad.name = "Road from 1,1 to 3,5"
		thisRoad.dir = "Up"
		thisRoad.points.append(CvtdRoadPoint(0, 0))
		thisRoad.points.append(CvtdRoadPoint(1, 10))
		thisRoad.points.append(CvtdRoadPoint(2, 20))
		thisRoad.points.append(CvtdRoadPoint(3, 30))
		thisRoad.points.append(CvtdRoadPoint(4, 40))
		thisRoad.points.append(CvtdRoadPoint(5, 50))
		myMap.roadList.append(thisRoad)
		
		thisRoad = CvtdRoad()
		thisRoad.name = "Road from 2,2 to 4,4"
		thisRoad.dir = "Up"
		thisRoad.points.append(CvtdRoadPoint(6, 0))
		thisRoad.points.append(CvtdRoadPoint(7, 10))
		thisRoad.points.append(CvtdRoadPoint(8, 20))
		thisRoad.points.append(CvtdRoadPoint(9, 30))
		myMap.roadList.append(thisRoad)

		intersections = myMap.find_intersecting_roads(0, 0)
		self.assertEqual(2, len(intersections))
	
	# def test_sort_filter_intersections(self):
	# 	myMap = CvtdMap()
	# 	myMap.nodeList.append(CvtdNode(1, 1))
	# 	myMap.nodeList.append(CvtdNode(4, 4))
	# 	myMap.nodeList.append(CvtdNode(1, 4))
	# 	myMap.nodeList.append(CvtdNode(4, 1))
	# 	myMap.nodeList.append(CvtdNode(3, 4))
	# 	myMap.nodeList.append(CvtdNode(4, 3))
		
	# 	thisRoad = CvtdRoad()
	# 	thisRoad.name = "Road from 1,1 to 4,4"
	# 	thisRoad.dir = "Up"
	# 	thisRoad.points.append(CvtdRoadPoint(0, 0))
	# 	thisRoad.points.append(CvtdRoadPoint(1, 60))
	# 	myMap.roadList.append(thisRoad)
		
	# 	thisRoad = CvtdRoad()
	# 	thisRoad.name = "Road from 1,4 to 4,1"
	# 	thisRoad.dir = "Up"
	# 	thisRoad.points.append(CvtdRoadPoint(2, 0))
	# 	thisRoad.points.append(CvtdRoadPoint(3, 60))
	# 	myMap.roadList.append(thisRoad)
		
	# 	thisRoad = CvtdRoad()
	# 	thisRoad.name = "Road from 3,4 to 4,3"
	# 	thisRoad.dir = "Up"
	# 	thisRoad.points.append(CvtdRoadPoint(4, 0))
	# 	thisRoad.points.append(CvtdRoadPoint(5, 50))
	# 	myMap.roadList.append(thisRoad)
		
	# 	intersections = myMap.find_intersecting_roads(0, 0)
	# 	self.assertEqual(2, len(intersections))
	# 	intersections1 = myMap.sort_filter_intersections(intersections, 1, 40)
	# 	self.assertEqual(1, len(intersections1))
	# 	intersections0 = myMap.sort_filter_intersections(intersections, 0, 40)
	# 	self.assertEqual(1, len(intersections0))
		
	# 	self.assertEqual(0, intersections1[0][0].roadIx)
	# 	self.assertEqual(30, intersections1[0][0].addr)
	# 	self.assertEqual(1, intersections1[0][1].roadIx)
	# 	self.assertEqual(30, intersections1[0][1].addr)
	# 	self.assertEqual(0, intersections0[0][0].roadIx)
	# 	self.assertEqual(50, intersections0[0][0].addr)
	# 	self.assertEqual(2, intersections0[0][1].roadIx)
	# 	self.assertEqual(25, intersections0[0][1].addr)

	def test_read_write_roads(self):
		myMap = CvtdMap()
		myMap.nodeList.append(CvtdNode(1, 1))
		myMap.nodeList.append(CvtdNode(4, 4))
		myMap.nodeList.append(CvtdNode(1, 4))
		myMap.nodeList.append(CvtdNode(4, 1))
		myMap.nodeList.append(CvtdNode(3, 4))
		myMap.nodeList.append(CvtdNode(4, 3))
		
		thisRoad = CvtdRoad()
		thisRoad.name = "Road from 0 to 60"
		thisRoad.dir = "Up"
		thisRoad.points.append(CvtdRoadPoint(0, 0))
		thisRoad.points.append(CvtdRoadPoint(1, 30))
		thisRoad.points.append(CvtdRoadPoint(2, 60))
		myMap.roadList.append(thisRoad)
		
		thisRoad = CvtdRoad()
		thisRoad.name = "Road from 0 to 60"
		thisRoad.dir = "Up"
		thisRoad.points.append(CvtdRoadPoint(1, 0))
		thisRoad.points.append(CvtdRoadPoint(3, 30))
		thisRoad.points.append(CvtdRoadPoint(4, 50))
		thisRoad.points.append(CvtdRoadPoint(5, 60))
		myMap.roadList.append(thisRoad)
		
		thisRoad = CvtdRoad()
		thisRoad.name = "Road from 0 to 50"
		thisRoad.dir = "Up"
		thisRoad.points.append(CvtdRoadPoint(0, 0))
		thisRoad.points.append(CvtdRoadPoint(5, 50))
		myMap.roadList.append(thisRoad)

		myMap.write_roads("tmp_roads.txt")

		myCmpMap = CvtdMap()
		myCmpMap.read_roads("tmp_roads.txt")

		self.assertEqual(len(myMap.nodeList), len(myCmpMap.nodeList))
		self.assertEqual(len(myMap.roadList), len(myCmpMap.roadList))

		self.assertEqual(myMap.nodeList[0].lat, myCmpMap.nodeList[0].lat)
		self.assertEqual(myMap.nodeList[0].lon, myCmpMap.nodeList[0].lon)
		self.assertEqual(myMap.nodeList[1].lat, myCmpMap.nodeList[1].lat)
		self.assertEqual(myMap.nodeList[1].lon, myCmpMap.nodeList[1].lon)
		self.assertEqual(myMap.nodeList[2].lat, myCmpMap.nodeList[2].lat)
		self.assertEqual(myMap.nodeList[2].lon, myCmpMap.nodeList[2].lon)
		self.assertEqual(myMap.nodeList[3].lat, myCmpMap.nodeList[3].lat)
		self.assertEqual(myMap.nodeList[3].lon, myCmpMap.nodeList[3].lon)
		self.assertEqual(myMap.nodeList[4].lat, myCmpMap.nodeList[4].lat)
		self.assertEqual(myMap.nodeList[4].lon, myCmpMap.nodeList[4].lon)
		self.assertEqual(myMap.nodeList[5].lat, myCmpMap.nodeList[5].lat)
		self.assertEqual(myMap.nodeList[5].lon, myCmpMap.nodeList[5].lon)

		self.assertEqual(myMap.roadList[0].name, myCmpMap.roadList[0].name)
		self.assertEqual(myMap.roadList[0].dir, myCmpMap.roadList[0].dir)
		self.assertEqual(myMap.roadList[0].points[0].node, myCmpMap.roadList[0].points[0].node)
		self.assertEqual(myMap.roadList[0].points[0].addr, myCmpMap.roadList[0].points[0].addr)
		self.assertEqual(myMap.roadList[0].points[1].node, myCmpMap.roadList[0].points[1].node)
		self.assertEqual(myMap.roadList[0].points[1].addr, myCmpMap.roadList[0].points[1].addr)
		self.assertEqual(myMap.roadList[0].points[2].node, myCmpMap.roadList[0].points[2].node)
		self.assertEqual(myMap.roadList[0].points[2].addr, myCmpMap.roadList[0].points[2].addr)
		self.assertEqual(myMap.roadList[1].name, myCmpMap.roadList[1].name)
		self.assertEqual(myMap.roadList[1].dir, myCmpMap.roadList[1].dir)
		self.assertEqual(myMap.roadList[1].points[0].node, myCmpMap.roadList[1].points[0].node)
		self.assertEqual(myMap.roadList[1].points[0].addr, myCmpMap.roadList[1].points[0].addr)
		self.assertEqual(myMap.roadList[1].points[1].node, myCmpMap.roadList[1].points[1].node)
		self.assertEqual(myMap.roadList[1].points[1].addr, myCmpMap.roadList[1].points[1].addr)
		self.assertEqual(myMap.roadList[1].points[2].node, myCmpMap.roadList[1].points[2].node)
		self.assertEqual(myMap.roadList[1].points[2].addr, myCmpMap.roadList[1].points[2].addr)
		self.assertEqual(myMap.roadList[1].points[3].node, myCmpMap.roadList[1].points[3].node)
		self.assertEqual(myMap.roadList[1].points[3].addr, myCmpMap.roadList[1].points[3].addr)
		self.assertEqual(myMap.roadList[2].name, myCmpMap.roadList[2].name)
		self.assertEqual(myMap.roadList[2].dir, myCmpMap.roadList[2].dir)
		self.assertEqual(myMap.roadList[2].points[0].node, myCmpMap.roadList[2].points[0].node)
		self.assertEqual(myMap.roadList[2].points[0].addr, myCmpMap.roadList[2].points[0].addr)
		self.assertEqual(myMap.roadList[2].points[1].node, myCmpMap.roadList[2].points[1].node)
		self.assertEqual(myMap.roadList[2].points[1].addr, myCmpMap.roadList[2].points[1].addr)

		os.remove("tmp_roads.txt")

if __name__ == '__main__':
	unittest.main()