####
# A simple class containing information about a specific bus
#
# busNumber -> Bus Number ?? Should this be included here? Is it constant? Or should it be pulled from the feed?
# routeNumber -> Route Number to expect to see on XML feed
# schedule -> Somehow we need to record the route's schedule
####
class CvtdBus:
	def __init__(self):
		self.busNumber = ""
		self.routeNumber = 0
		self.schedule = None
	
	def __init__(self, busNumber, routeNumber):
		self.busNumber = busNumber
		self.routeNumber = routeNumber
		self.schedule = None
		
