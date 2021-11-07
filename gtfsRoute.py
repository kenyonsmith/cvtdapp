####
# A class representing a route according to the GTFS standard
#  NOTE: routeId is not included here since it is typically the key to a route dictionary
#
# agencyId is the agency that this route belongs to
# routeShortName is the short name of the route, i.e. "1"
# routeLongName is the long name of the route, i.e. "USU, NE Logan 1600 E"
# routeDesc is a description of the route (optional)
# routeType is the type of service (0=Tram, 3=Bus, etc)
#  For more info, see https://developers.google.com/transit/gtfs/reference#routestxt
####
class GtfsShape:
  def __init__(self):
    self.agencyId = None
    self.routeShortName = None
    self.routeLongName = None
    self.routeType = None

  ####
  # describe prints all information about this route
  ####
  def describe(self):
    print(f"{self.routeShortName}: {self.routeLongName}, Agency {self.agencyId")

  ####
  # validate checks to see if the route is valid
  ####
  def validate(self):
    return True

  ####
  # findTrip searches for the matching trip given a date and this route
  #
  # date Date to search the calendar list for a service Id
  # calendarList list of calendar entries from the map
  # tripList list of trips from the map
  #
  # returns trip ID of current trip
  ####
  def findTrip(self, date, calendarList, tripList):
    # First, find what calendar entry to use
    calendarServiceId = None
    for serviceId in calendarList:
      if calendarList[serviceId].dateWithinCalendarEntry(date):
        calendarServiceId = serviceId
        break

    # This is the right calendar entry, now find the right trip
    if calendarServiceId != None:
      for tripId in tripList:
        if tripList[tripId].serviceId == calendarServiceId:
          return tripId
    return None
  
  ####
  # findShape finds the shape that matches this route
  #
  # date is the date to find a shape for (used to search Trips)
  # shapeList is the list of Shapes
  # calendarList is the list of CalendarEntries
  # tripList is the list of Trips
  #
  # returns shape ID of the matching shape, or None
  ####
  def findShape(self, date, shapeList, calendarList, tripList):
    tripId = self.findTrip(date, calendarList, tripList)
    if tripId is not None:
      shapeId = tripList[tripId]
      while shapeList[shapeId].copyOfId is not None:
        shapeId = shapeList[shapeId].copyofId
      return shapeId
    return None


