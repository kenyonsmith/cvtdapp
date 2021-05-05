import xml.etree.ElementTree as ET

####
# A class containing information about buses and their locations
#
# pos -> A dictionary, where key is 4-digit bus number and value is a list of CvtdBusPosition's, sorted by timestamp
####
class CvtdBusLocator:
	def __init__(self):
		self.pos = {}
	
	####
	# insert inserts a position into the locator such that CvtdBusPosition arrays are always sorted by timestamp
	#
	# key is the key of the bus into the pos dictionary, the 4-digit bus number
	# position is the CvtdBusPosition object to be inserted
	####
	def insert(self, key, position):
		# Add the key to self.pos if it is not there
		if key not in self.pos:
			self.pos[key] = []
		
		# If the position list is empty, or if the new timestamp will go at the end, no need to look for the right place to put it
		if len(self.pos[key]) == 0 or position.timestamp > self.pos[key][-1].timestamp:
			self.pos[key].append(position)
		else:
			# Starting at the back of the array, search backwards until we find a place where the past timestamp is greater
			ix = len(self.pos[key]) - 2
			while ix >= 0:
				if position.timestamp > self.pos[key][ix].timestamp:
					# We went back too far, go forward one spot
					self.pos[key].insert(ix+1, position)
					break
				elif position.timestamp == self.pos[key][ix].timestamp:
					# We found an exact match, don't bother adding
					return
				ix -= 1
			if ix == -1:
				self.pos[key].insert(0, position)
	
	####
	# find_next_after returns the CvtdBusPosition after a given timestamp
	#
	# key is the key of the bus into the pos dictionary
	# timestamp is the timestamp to find next position after
	#
	# return is the CvtdBusPosition, or None if none exists
	####
	def find_next_after(self, key, timestamp):
		ix = 0
		while ix < len(self.pos[key]):
			if self.pos[key][ix].timestamp > timestamp:
				return self.pos[key][ix]
			ix += 1
	
	####
	# find_next_before returns the CvtdBusPosition before a given timestamp
	#
	# key is the key of the bus into the pos dictionary
	# timestamp is the timestamp to find position before
	#
	# return is the CvtdBusPosition, or None if none exists
	####
	def find_next_before(self, key, timestamp):
		ix = len(self.pos[key])-1
		while ix >= 0:
			if self.pos[key][ix].timestamp < timestamp:
				return self.pos[key][ix]
			ix -= 1

	####
	# find searches for a bus position exactly matching the given timestamp
	#
	# key is the key of the bus into the pos dictionary
	# timestamp is the timestamp to find position for
	#
	# return is the CvtdBusPosition, or None if none exists
	####
	def find(self, key, timestamp):
		try:
			ix = len(self.pos[key])-1
			while ix >= 0:
				if self.pos[key][ix].timestamp == timestamp:
					return self.pos[key][ix]
				ix -= 1
		except KeyError:
			return None
