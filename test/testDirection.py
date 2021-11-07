import unittest

import inspect
import os
import sys
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

import direction
from direction import Direction

class TestDirection(unittest.TestCase):
	def test_get_direction(self):
		self.assertEqual(Direction.N, direction.get_direction(0))
		self.assertEqual(Direction.N, direction.get_direction(12))
		self.assertEqual(Direction.N, direction.get_direction(22))
		self.assertEqual(Direction.NE, direction.get_direction(23))
		self.assertEqual(Direction.NE, direction.get_direction(60))
		self.assertEqual(Direction.E, direction.get_direction(90))
		self.assertEqual(Direction.SE, direction.get_direction(130))
		self.assertEqual(Direction.S, direction.get_direction(170))
		self.assertEqual(Direction.SW, direction.get_direction(215))
		self.assertEqual(Direction.W, direction.get_direction(280))
		self.assertEqual(Direction.NW, direction.get_direction(300))
		self.assertEqual(Direction.N, direction.get_direction(355))

if __name__ == '__main__':
	unittest.main()