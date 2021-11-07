import inspect
import os
import sys
import unittest

import datetime

from direction import Direction

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

from cvtdBusPosition import CvtdBusPosition

class TestCvtdBusPosition(unittest.TestCase):
    def test_package_unpackage(self):
        now = datetime.datetime.now()
        now_sec = datetime.datetime(now.year, now.month, now.day, now.hour, now.minute, now.second, 0)
        pos = CvtdBusPosition(now_sec, 12.467, -136.51, 0)
        b = pos.package()
        pos2 = CvtdBusPosition(b)

        self.assertEqual(pos.timestamp, pos2.timestamp)
        self.assertAlmostEqual(pos.lat, pos2.lat, 1)
        self.assertAlmostEqual(pos.lon, pos2.lon, 1)
        self.assertEqual(pos.direction, pos2.direction)

if __name__ == '__main__':
	unittest.main()