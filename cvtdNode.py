####
# A simple class holding latitude and longitude
#
# lat -> Latitude
# lon -> Longitude
####
class CvtdNode:
	def __init__(self):
		self.lat = 0
		self.lon = 0
	
	def __init__(self, lat, lon):
		self.lat = lat
		self.lon = lon
