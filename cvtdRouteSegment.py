####
# A class representing a segment on a route
#
# roadIx -> Index into some roadList that specifies which road this segment lies on
# beginAddr -> Address at which this segment begins
# endAddr -> Address at which this segment ends
####
class CvtdRouteSegment:
	def __init__(self):
		self.roadIx = None
		self.beginAddr = None
		self.endAddr = None

	def __init__(self, roadIx, beginAddr, endAddr):
		self.roadIx = roadIx
		self.beginAddr = beginAddr
		self.endAddr = endAddr