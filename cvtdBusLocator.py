import xml.etree.ElementTree as ET

####
# A class containing information about buses and their locations
#
# pos -> A dictionary, where key is bus identifier and value is a list of CvtdBusPosition's
####
class CvtdBusLocator:
	def __init__(self):
		self.pos = {}
	
	####
	# insert inserts a position into the locator such that CvtdBusPosition arrays are always sorted by timestamp
	#
	# key is the key of the bus into the pos dictionary
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
				ix -= 1
			if ix == -1:
				self.pos[key].insert(0, position)
	
	def find_next_after(self, key, timestamp):
		ix = 0
		while ix < len(self.pos[key]):
			if self.pos[key][ix].timestamp > timestamp:
				return self.pos[key][ix]
			ix += 1
	
	def find_next_before(self, key, timestamp):
		ix = len(self.pos[key])-1
		while ix >= 0:
			if self.pos[key][ix].timestamp < timestamp:
				return self.pos[key][ix]
			ix -= 1
	
	def parse_cvtd_feed(self, filename):
		tree = ET.parse(filename)
		root = tree.getroot()
		for bus in root:
			for i in range(NUM_ELEMENTS - 1, 0, -1):
				try:
					bnum = bus[3].text
					route = bus[5].text
					t = bus[8][i].text.strip().split()[1].split('.')[0]
					lat = float(bus[8][i][0].text)
					lon = float(bus[8][i][1].text)
					direction = int(bus[8][i][2].text)
					if lat == 0.0 and lon == 0.0:
						continue
				except IndexError:
					continue
