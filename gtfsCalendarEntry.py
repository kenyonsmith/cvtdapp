####
# A class representing a calendar entry according to the GTFS standard
#  NOTE: service id is not included here since it is typically the key to a calendar dictionary
#
# id is the unique ID of this shape
# daysOfWeek is a 7-bit integer indicating what days of the week this calendar applies to
#  Monday is the least significant bit
# startDate is a DateTime object. This calendar entry becomes valid on this date.
# endDate is a DateTime object. This calendar entry is valid until this date.
####
class GtfsCalendarEntry:
  def __init__(self):
    self.daysOfWeek = 0
    self.startDate = None
    self.endDate = None

  ####
  # describe prints all information about this shape
  ####
  def describe(self):
    print(f"Calendar from {self.startDate} to {self.endDate}")

  ####
  # dayOfWeek returns True if the schedule is valid on this day of week, else False
  #
  # dayOfWeek is 1 for Monday, 7 for Sunday
  #
  # return True if schedule is valid, else False
  ####
  def dayOfWeek(self, dayOfWeek):
    return self.daysOfWeek & (1 << (dayOfWeek - 1)) != 0

  ####
  # generateDaysOfWeek sets daysOfWeek variable based on specifications
  # 
  # monday is whether this schedule is valid on Monday (True or False)
  # tuesday is whether this schedule is valid on Tuesday (True or False)
  # wednesday is whether this schedule is valid on Wednesday (True or False)
  # thursday is whether this schedule is valid on Thursday (True or False)
  # friday is whether this schedule is valid on Friday (True or False)
  # saturday is whether this schedule is valid on Saturday (True or False)
  # sunday is whether this schedule is valid on Sunday (True or False)
  ####
  def generateDaysOfWeek(self, monday, tuesday, wednesday, thursday, friday, saturday, sunday):
    self.daysOfWeek = 0
    if monday:
      self.daysOfWeek |= 1
    if tuesday:
      self.daysOfWeek |= 2
    if wednesday:
      self.daysOfWeek |= 4
    if thursday:
      self.daysOfWeek |= 8
    if friday:
      self.daysOfWeek |= 16
    if saturday:
      self.daysOfWeek |= 32
    if sunday:
      self.daysOfWeek |= 64

  ####
  # validate checks to see if the calendar entry is valid
  ####
  def validate(self):
    if self.endDate > self.startDate and self.daysOfWeek != 0:
      return True
    return False

  ####
  # dateWithinCalendarEntry checks to see if a date falls on this calendar entry
  #
  # date is a DateTime object
  #
  # return is True if the date is within the calendar entry, else False
  ####
  def dateWithinCalendarEntry(self, date):
    if self.startDate.year <= date.year <= self.endDate.year:
      if self.startDate.month <= date.month <= self.endDate.month:
        if self.startDate.day <= date.day <= self.endDate.day:
          if self.dayOfWeek(date.isoweekday()):
            return True
    return False
