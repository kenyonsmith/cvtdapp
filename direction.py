import enum

LONG_STRING_DICT = {"N": "North", "E": "East", "S": "South", "W": "West", "NE": "Northeast", "SE": "Southeast", "SW": "Southwest", "NW": "Northwest", "X": "Stopped"}

####
# An enumeration of the different directions
####
class Direction(enum.Enum):
	N = enum.auto()
	E = enum.auto()
	S = enum.auto()
	W = enum.auto()
	NE = enum.auto()
	NW = enum.auto()
	SE = enum.auto()
	SW = enum.auto()
	X = enum.auto()
	
	def short_str(self):
		return self.name
	
	def long_str(self):
		return LONG_STRING_DICT[self.name]

HEADING_DICT = {0: Direction.N, 45: Direction.NE, 90: Direction.E, 135: Direction.SE, 180: Direction.S, 225: Direction.SW, 270: Direction.W, 315: Direction.NW, 360: Direction.N}

####
# get_direction finds the closest direction from "N" through "SW" to a heading in degrees
#
# d is the heading in degrees
#
# return is the string representatino of the direction
####
def get_direction(d):
	d = round(d / 45) * 45
	return HEADING_DICT[d]

