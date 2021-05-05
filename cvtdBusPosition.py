####
# A simple class containing information about a specific bus's ping location
#
# timestamp -> datetime.datetime.Datetime associated with this ping
# lat -> latitude of the ping
# lon -> longitude of the ping
# direction -> direction (as integer from 0 to 360) indicated by XML pull, or calculated
####
class CvtdBusPosition:
	def __init__(self):
		self.timestamp = None
		self.lat = 0
		self.lon = 0
		self.direction = None
	
	def __init__(self, timestamp, lat, lon, direction):
		self.timestamp = timestamp
		self.lat = lat
		self.lon = lon
		self.direction = direction
		

