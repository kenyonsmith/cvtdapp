####
# An object representing a stop, (stop ID is the key)
#
# name -> Short name of this stop
# description -> Longer description of stop location
# lat -> Latitude
# lon -> Longitude
####
class CvtdRouteStop:
	def __init__(self):
		self.name = ""
		self.description = ""
		self.lat = 0
		self.lon = 0
	
	def __init__(self, stopId, name, description, lat, lon):
		self.name = name
		self.description = description
		self.lat = lat
		self.lon = lon

