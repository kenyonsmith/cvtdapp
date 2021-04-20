from cvtdUtil import CvtdUtil

####
# A class representing a point on a road, including the index of the road (not for storage)
#
# addr -> Numerical address at this point, positive for N or E and negative for S or W
# roadIx -> Index of the road that this point lies on
####
class ContainedRoadPoint:
	def __init__(self):
		self.addr = 0
		self.roadIx = 0
	
	def __init__(self, addr, roadIx):
		self.addr = addr
		self.roadIx = roadIx

	####
	# addr_dir returns the address and direction representation of the point, ex. "1334 N"
	#
	# self is the ContainedRoadPoint
	# roadList is the array of Roads that roadIx indexes into
	#
	# return is the string representation of the address and the direction
	####
	def addr_dir(self, roadList):
		return CvtdUtil.addr_dir(self.addr, roadList[self.roadIx].dir)
	
	####
	# addr_repr returns the address, direction and street name representation, ex. "1334 N Main Street"
	#
	# self is the ContainedRoadPoint
	# roadList is the array of Roads that roadIx indexes into
	#
	# return is the string representation of the address, direction and street name
	#####
	def addr_repr(self, roadList):
		return CvtdUtil.addr_repr(self.addr, roadList[self.roadIx].dir, roadList[self.roadIx].name)
