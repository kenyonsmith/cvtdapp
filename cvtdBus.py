####
# A simple class containing information about a specific bus
#
# routeId -> An integer value with the route ID
# routeNumber -> Route Number to expect to see on XML feed, not guaranteed to be an integer, i.e. "B2" or "3"
# schedule -> Somehow we need to record the route's schedule, so we can know if it is on detour, early or late
####
class CvtdBus:
	def __init__(self, routeId, routeNumber):
		self.routeId = routeId
		self.routeNumber = routeNumber
		self.schedule = None
		

