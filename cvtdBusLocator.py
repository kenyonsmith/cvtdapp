import os
import struct
import xml.etree.ElementTree as ET

from cvtdBusPosition import CvtdBusPosition
from cvtdBusPosition import pack_string

####
# A class containing information about buses and their locations
#
# pos -> A dictionary, where key is route number and value is a list of CvtdBusPosition's, sorted by timestamp
# dirPath -> Path to the directory where position information will be stored, with no final '/' (removed by init)
####
class CvtdBusLocator:
	def __init__(self, dirPath=None):
		self.pos = {}
		self.dirPath = dirPath
		if dirPath:
			while self.dirPath[-1] == '/':
				self.dirPath = self.dirPath[:-1]
	
	####
	# insert inserts a position into the locator such that CvtdBusPosition arrays are always sorted by timestamp
	#
	# key is the key of the bus into the pos dictionary, the route number
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

	####
	# read_locator opens all files in self.dirPath and attempts to read them
	####
	def read_locator(self):
		if self.dirPath:
			for filename in os.listdir(self.dirPath):
				# File will be some/path/route_XYZ.dat. We want the XYZ
				rnum = filename.split('/')[-1][6:-4]
				with open("/".join((self.dirPath, filename)), 'rb') as f:
					data = f.read()
				offset = 0
				packsize = struct.calcsize(pack_string)
				while offset + packsize <= len(data):
					b = data[offset:offset+packsize]
					self.insert(rnum, CvtdBusPosition(b))
					offset = offset + packsize

	####
	# write_locator writes all of the buses in the locator to dirPath, i.e. "route_1.dat"
	####
	def write_locator(self):
		if self.dirPath:
			for key in self.pos:
				with open('/'.join((self.dirPath, f"route_{key}.dat")), 'wb') as f:
					for position in self.pos[key]:
						f.write(position.package())
	
	####
	# append_position_to_file is called to write a single new position to a file
	#
	# key is the route number of the position, or key into self.pos
	# position is the CvtdBusPosition object
	####
	def append_position_to_file(self, key, position):
		if self.dirPath:
			with open('/'.join((self.dirPath, f"route_{key}.dat")), 'ab') as f:
				f.write(position.package())

	####
	# insert_append calls the respective calls on a given position.
	#  NOTE: insert_append should ONLY be called when the position to be added will finish last in the locator
	#
	# TODO: insert into the file if the position is not at the end
	#
	# key is the route number of the position, or key into self.pos
	# position is the CvtdBusPosition object
	####
	def insert_append(self, key, position):
		self.insert(key, position)
		self.append_position_to_file(key, position)