####
# A class representing a trip according to the GTFS standard
#  NOTE: tripId is not included here since it is typically the key to a trip dictionary
#
# routeId is an integer indicating to which route this trip applies
# serviceId is a string indicating to which calendar entry this trip applies
# directionId is an integer indicating direction of this trip (usage?)
# blockId is a string indicating this block id (usage?) (must be string, not int)
# shapeId is an integer indicating shape that goes with this trip
####
class GtfsTrip:
  def __init__(self):
    self.routeId = None
    self.serviceId = None
    self.directionId = None
    self.blockId = None
    self.shapeId = None

  ####
  # describe prints all information about this shape
  ####
  def describe(self):
    print(f"Route ID is {self.routeId}")
    print(f"Service ID is {self.serviceId}")
    print(f"Direction ID is {self.directionId}")
    print(f"Block ID is {self.blockId}")
    print(f"Shape ID is {self.shapeId}")

  ####
  # validate checks to see if the shape is valid
  ####
  def validate(self):
    return True
