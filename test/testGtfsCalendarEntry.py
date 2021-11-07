import inspect
import os
import sys
import unittest

import datetime

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

from gtfsCalendarEntry import GtfsCalendarEntry

class TestGtfsCalendarEntry(unittest.TestCase):
    def test_days_of_week(self):
        cal = GtfsCalendarEntry()
        cal.generateDaysOfWeek(1, 1, 0, 1, 1, 0, 0)
        self.assertTrue(cal.dayOfWeek(1))
        self.assertTrue(cal.dayOfWeek(2))
        self.assertFalse(cal.dayOfWeek(3))
        self.assertTrue(cal.dayOfWeek(4))
        self.assertTrue(cal.dayOfWeek(5))
        self.assertFalse(cal.dayOfWeek(6))
        self.assertFalse(cal.dayOfWeek(7))

        cal.generateDaysOfWeek(0, 0, 0, 1, 1, 1, 0)
        self.assertFalse(cal.dayOfWeek(1))
        self.assertFalse(cal.dayOfWeek(2))
        self.assertFalse(cal.dayOfWeek(3))
        self.assertTrue(cal.dayOfWeek(4))
        self.assertTrue(cal.dayOfWeek(5))
        self.assertTrue(cal.dayOfWeek(6))
        self.assertFalse(cal.dayOfWeek(7))
        
        cal.generateDaysOfWeek(1, 1, 1, 1, 1, 1, 1)
        self.assertTrue(cal.dayOfWeek(1))
        self.assertTrue(cal.dayOfWeek(2))
        self.assertTrue(cal.dayOfWeek(3))
        self.assertTrue(cal.dayOfWeek(4))
        self.assertTrue(cal.dayOfWeek(5))
        self.assertTrue(cal.dayOfWeek(6))
        self.assertTrue(cal.dayOfWeek(7))
        
        cal.generateDaysOfWeek(0, 0, 0, 0, 0, 0, 0)
        self.assertFalse(cal.dayOfWeek(1))
        self.assertFalse(cal.dayOfWeek(2))
        self.assertFalse(cal.dayOfWeek(3))
        self.assertFalse(cal.dayOfWeek(4))
        self.assertFalse(cal.dayOfWeek(5))
        self.assertFalse(cal.dayOfWeek(6))
        self.assertFalse(cal.dayOfWeek(7))

    def test_date_within(self):
        cal = GtfsCalendarEntry()
        cal.generateDaysOfWeek(1, 1, 0, 0, 0, 0, 1)
        cal.startDate = datetime.date(2021, 6, 21)
        cal.endDate = datetime.date(2021, 6, 27)

        # June 21, 2021 is a Monday

        self.assertFalse(cal.dateWithinCalendarEntry(datetime.date(2021, 6, 19)))
        self.assertFalse(cal.dateWithinCalendarEntry(datetime.date(2021, 6, 20)))
        self.assertTrue(cal.dateWithinCalendarEntry(datetime.date(2021, 6, 21)))
        self.assertTrue(cal.dateWithinCalendarEntry(datetime.date(2021, 6, 22)))
        self.assertFalse(cal.dateWithinCalendarEntry(datetime.date(2021, 6, 23)))
        self.assertFalse(cal.dateWithinCalendarEntry(datetime.date(2021, 6, 24)))
        self.assertFalse(cal.dateWithinCalendarEntry(datetime.date(2021, 6, 25)))
        self.assertFalse(cal.dateWithinCalendarEntry(datetime.date(2021, 6, 26)))
        self.assertTrue(cal.dateWithinCalendarEntry(datetime.date(2021, 6, 27)))
        self.assertFalse(cal.dateWithinCalendarEntry(datetime.date(2021, 6, 28)))

if __name__ == '__main__':
	unittest.main()