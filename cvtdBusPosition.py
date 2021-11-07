import datetime
import struct
import time

####
# Pack string used for struct packing and unpacking
####
pack_string = "@LffH"

####
# A simple class containing information about a specific bus's ping location
#
# timestamp -> datetime.datetime.Datetime associated with this ping
# lat -> latitude of the ping
# lon -> longitude of the ping
# direction -> direction (as integer from 0 to 360) indicated by XML pull, or calculated. Note: This is NOT an instance of the Direction class
####
class CvtdBusPosition:
	def __init__(self, *args):
		if len(args) == 1 and isinstance(args[0], bytes):
			# Unpackage, or the inverse of package()
			stamp, lat, lon, direction = struct.unpack("@LffH", args[0])
			self.timestamp = datetime.datetime.fromtimestamp(stamp)
			self.lat = lat
			self.lon = lon
			self.direction = direction
		elif len(args) == 4 and isinstance(args[0], datetime.datetime) and isinstance(args[1], float) and isinstance(args[2], float) and isinstance(args[3], int):
			self.timestamp = args[0]
			self.lat = args[1]
			self.lon = args[2]
			self.direction = args[3]
		elif len(args) == 0:
			self.timestamp = None
			self.lat = 0.0
			self.lon = 0.0
			self.direction = None
		else:
			raise AttributeError("CvtdBusPosition constructor was called with invalid arguments")

	####
	# package packages the position value into a series of bytes to be written into a locator file
	#
	# return is the bytes() object to write to the binary file
	####
	def package(self):
		stamp = time.mktime(self.timestamp.timetuple())
		try:
			b = struct.pack("@LffH", int(stamp), self.lat, self.lon, self.direction)
		except struct.error:
			print(f"Struct Error. Stamp is {stamp}, lat is {self.lat}, lon is {self.lon}, dir is {self.direction}")
			raise
		return b
