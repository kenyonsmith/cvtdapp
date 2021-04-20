####
# A class representing a route
#
# name -> Unique name used to identify this route, (i.e. "Route 3", "Blue Loop")
# buses -> List of Bus objects that use this route (many times there will only be one)
# segments -> List of RouteSegment objects that delineate this route
# stops -> List of RouteStop objects on this route
####
class CvtdRoute:
	def __init__(self):
		self.name = ""
		self.buses = []
		self.segments = []
		self.stops = []

####
# compute_route_completion 
# points
# segment_ix
# segment_percent is a number between 0 and 1, representing the completed portion of the segment
#
# return[0] is the percent route completion, as a number between 0 and 1
####
#def compute_route_completion(self, points, segment_ix, segment_percent):
#	distances = []
#	for ix, segment in enumerate(points):
#		blat1 = ROAD_LIST[segment[0]][S_BLAT]
#		blon1 = ROAD_LIST[segment[0]][S_BLON]
#		elat1 = ROAD_LIST[segment[0]][S_ELAT]
#		elon1 = ROAD_LIST[segment[0]][S_ELON]
#		dlat1 = abs(elat1 - blat1)
#		dlon1 = abs(elon1 - blon1)
#
#		nsegment = points[ix + 1 if (ix + 1) < len(points) else 0]
#		blat2 = ROAD_LIST[nsegment[0]][S_BLAT]
#		blon2 = ROAD_LIST[nsegment[0]][S_BLON]
#		elat2 = ROAD_LIST[nsegment[0]][S_ELAT]
#		elon2 = ROAD_LIST[nsegment[0]][S_ELON]
#		dlat2 = abs(elat2 - blat2)
#		dlon2 = abs(elon2 - blon2)
#
#		if segment[0] == nsegment[0]:
#			# Great, we're measuring distance between two points on the same road
#			this_lat = (nsegment[1] - segment[1]) * dlat1
#			this_lon = (nsegment[1] - segment[1]) * dlon1
#			distance = math.sqrt(this_lat * this_lat + this_lon * this_lon)
#			distances.append(distance)
#		else:
#			# Sum the distance travelled on the two segments
#			this_lat = (1 - segment[1]) * dlat1
#			this_lon = (1 - segment[1]) * dlon1
#			distance1 = math.sqrt(this_lat * this_lat + this_lon * this_lon)
#
#			this_lat = nsegment[1] * dlat1
#			this_lon = nsegment[1] * dlon1
#			distance2 = math.sqrt(this_lat * this_lat + this_lon * this_lon)
#
#			distance = distance1 + distance2
#			distances.append(distance)
#
#	total_distance = sum(distances)
#	distance_travelled = sum(distances[:segment_ix]) + (segment_percent * distances[segment_ix])
#	return distance_travelled / total_distance

####
# print_segments prints out each segment in the route
#
# roadList is the RoadList referred to by the route's segments
####
def print_segments(self, roadList):
	for segment in this_route.segments:
		segRoad = roadList[segment.roadIx]
		s = f" - {segRoad.name} from {CvtdUtil.addr_dir(segment.beginAddr, segRoad.dir)} to {CvtdUtil.addr_dir(segment.endAddr, segRoad.dir)}"
		print(s)
