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

	def __str__(self):
		return f"{self.lat}, {self.lon}"
	
	####
	# compare_node compares two nodes and returns True if they are practically identical
	#
	# otherNode is the other CvtdNode to compare
	#
	# return True if they match, False if they do not
	####
	def compare_node(self, otherNode):
		return (abs(self.lat - otherNode.lat) < 0.000001) and (abs(self.lon - otherNode.lon) < 0.000001)
