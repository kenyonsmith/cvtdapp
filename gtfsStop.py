# stop_id,stop_code,stop_name,stop_desc,stop_lat,stop_lon,zone_id,stop_url,location_type,parent_station,stop_timezone,wheelchair_boarding
# 100,,Intermodal Transit Center,,41.740696,-111.830901,,,1,,,
# 101,,150 East 500 North(Transit Center),,41.740788,-111.830626,,,0,100,,



####
# A class representing a stop according to the GTFS standard
#  NOTE: stopId is not included here since it is typically the key to a stop dictionary
#
# stopCode is an optional integer that is public-facing and used to identify this stop. If ID is public-facing, this is blank
# stopName is the name of this stop
# lat is the latitude of this stop
# lon is the longitude of this stop
# locationType is the type of location (1=station, 0=stop)
# parentStation is the "home" station of this stop
####
class GtfsStop:
  def __init__(self):
    self.stopCode = None
    self.stopName = ''
    self.lat = 0.0
    self.lon = 0.0
    self.locationType = None
    self.parentStation = None

  ####
  # describe prints all information about this stop
  ####
  def describe(self):
    pass

  ####
  # validate checks to see if the shape is valid
  ####
  def validate(self):
    if self.locationType == 1:
      return self.parentStation is None
    elif self.locationType in [1, 2]:
      return self.parentStation is not None
    return True
