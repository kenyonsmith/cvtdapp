####
# A class representing a calendar date according to the GTFS standard
#
# serviceId is the Calendar Entry ID associated with this object
# date is the date used in this object
# exception type is unknown type
####
class GtfsShape:
  def __init__(self):
    self.serviceId = None
    self.date = None
    self.exceptionType = None

  ####
  # describe prints all information about this calendar date
  ####
  def describe(self):
    pass

  ####
  # validate checks to see if the calendar date is valid
  ####
  def validate(self):
    return True
