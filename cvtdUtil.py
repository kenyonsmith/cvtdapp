import math

####
# A "static" class of utility methods
####
class CvtdUtil:
	####
	# sub_proj_ratio calculates the distance from a point to either the beginning or end of a street, whichever is further
	#
	# lat is the latitude of the point to locate
	# lon is the longitude of the point to locate
	# blat is the latitude of the beginning of the street
	# blon is the longitude of the beginning of the street
	# elat is the latitude of the end of the street
	# elon is the longitude of the end of the street
	#
	# return[0] is the Pythagorean length of the street
	# return[1] is the Pythagorean difference between the point and the beginning/end of the street
	# return[2] is return[1] projected onto return[0] (equals 0 for no correlation, return[0] if max correlation)
	# return[3] is 1 if the beginning was further, 0 if the end was further
	####
	def sub_proj_ratio(lat, lon, blat, blon, elat, elon):
		blat_diff = lat-blat
		blon_diff = lon-blon
		elat_diff = lat-elat
		elon_diff = lon-elon

		st_begin_dist = math.sqrt(blat_diff * blat_diff + blon_diff * blon_diff)
		st_end_dist = math.sqrt(elat_diff * elat_diff + elon_diff * elon_diff)

		if st_begin_dist > st_end_dist:
			street_lat = elat - blat
			street_lon = elon - blon
			pos_lat = lat - blat
			pos_lon = lon - blon
			begin_or_end = 1
		else:
			street_lat = blat - elat
			street_lon = blon - elon
			pos_lat = lat - elat
			pos_lon = lon - elon
			begin_or_end = 0

		street_sc = math.sqrt(street_lat * street_lat + street_lon * street_lon)
		pos_sc =  math.sqrt(pos_lat * pos_lat + pos_lon * pos_lon)
		try:
			projection_sc = ((pos_lat * street_lat) + (pos_lon * street_lon)) / ((street_lat * street_lat) + (street_lon * street_lon)) * street_sc
		except ZeroDivisionError:
			projection_sc = 0.0
			print(f"Error [sub_proj_ratio]: Start and end point are equal: {blat} {blon} = {elat} {elon}")

		return street_sc, pos_sc, projection_sc, begin_or_end

	####
	# coord_to_ft converts a difference in two GPS coordinates, either lat or lon, to feet
	#
	# return is the approximate difference in feet
	####
	def coord_to_ft(coord):
		return coord*70*5280
	
	####
	# addr_dir returns the address and direction representation of a point, ex. "1334 N"
	#
	# addr is the address of the point
	# dir is the direction of the road the point lies on
	#
	# return is the string representation of the address and the direction
	####
	def addr_dir(addr, dir):
		if dir == "N/S":
			if addr > 0:
				nesw = "N"
			else:
				nesw = "S"
		elif dir == "E/W":
			if addr > 0:
				nesw = "E"
			else:
				nesw = "W"
		else:
			nesw = dir
		return f"{abs(addr)} {nesw}"
	
	####
	# addr_repr returns the address, direction and street name representation, ex. "1334 N Main Street"
	#
	# addr is the address of the point
	# dir is the direction of the road the point lies on
	# name is the name of the road the point lies on
	#
	# return is the string representation of the address, direction and street name
	#####
	def addr_repr(addr, dir, name):
		return f"{CvtdUtil.addr_dir(addr, dir)} {name}"
		
	####
	# get_line_intersection() returns the lat and lon positions of the intersection, or None
	#
	# node1 is the CvtdNode object representing the starting node
	# node2 is the CvtdNode object representing the starting node
	#
	# returns [lat, lon] or None if there is no intersection
	####
	def get_line_intersection(n1s, n1e, n2s, n2e):
		Ax1 = n1s.lat
		Ay1 = n1s.lon
		Ax2 = n1e.lat
		Ay2 = n1e.lon
		Bx1 = n2s.lat
		By1 = n2s.lon
		Bx2 = n2e.lat
		By2 = n2e.lon

		d = (By2 - By1) * (Ax2 - Ax1) - (Bx2 - Bx1) * (Ay2 - Ay1)
		if d:
			uA = ((Bx2 - Bx1) * (Ay1 - By1) - (By2 - By1) * (Ax1 - Bx1)) / d
			uB = ((Ax2 - Ax1) * (Ay1 - By1) - (Ay2 - Ay1) * (Ax1 - Bx1)) / d
		else:
			return
		if not(0 <= uA <= 1 and 0 <= uB <= 1):
			return
		x = Ax1 + uA * (Ax2 - Ax1)
		y = Ay1 + uA * (Ay2 - Ay1)
	 
		return x, y
