####
# A class representing a point on a road, with a node and associated address
#
# node -> Index into associated NODE_LIST of this point
# addr -> Numerical address at this point, positive for N or E and negative for S or W
####
class CvtdRoadPoint:
	def __init__(self):
		self.node = 0
		self.addr = 0

	def __init__(self, node, addr):
		self.node = node
		self.addr = addr

