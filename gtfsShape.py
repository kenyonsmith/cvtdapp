####
# A class representing a shape according to the GTFS standard
#  NOTE: shapeId is not included here since it is typically the key to a shape dictionary
#
# copyOfId is a unique ID of a shape of which this is an exact copy, or None
# pointList is a list of CvtdNode objects, or [] if copyOfId is not None
####
class GtfsShape:
  def __init__(self):
    self.copyOfId = None
    self.pointList = []

  ####
  # describe prints all information about this shape
  ####
  def describe(self):
    if self.copyOfId is not None:
      print("Copy of Shape with Id: " + self.copyOfId)
    else:
      for point in self.pointList:
        print(f"{point.lat}, {point.lon}")

  ####
  # validate checks to see if the shape is valid
  ####
  def validate(self):
    if self.copyOfId is not None:
      return self.copyOfId != self.id
    else:
      # Check to make sure that each point in self.pointList is a CvtdNode
      for point in self.pointList:
        if not isinstance(point, CvtdNode):
          return False
    return True

  ####
  # compare_point_list compares a given point list with that of this shape
  #
  # pointList is the point list to compare to the point list of this shape
  #
  # return is True if all points are in the same order, else False
  ####
  def compare_point_list(self, pointList):
    return [x.lat for x in self.pointList] == [x.lat for x in pointList] and [x.lon for x in self.pointList] == [x.lon for x in pointList]

####
# compute_route_completion 
# points
# segment_ix
# segment_percent is a number between 0 and 1, representing the completed portion of the segment
#
# return[0] is the percent route completion, as a number between 0 and 1
####
#def compute_route_completion(self, points, segment_ix, segment_percent):
#  distances = []
#  for ix, segment in enumerate(points):
#    blat1 = ROAD_LIST[segment[0]][S_BLAT]
#    blon1 = ROAD_LIST[segment[0]][S_BLON]
#    elat1 = ROAD_LIST[segment[0]][S_ELAT]
#    elon1 = ROAD_LIST[segment[0]][S_ELON]
#    dlat1 = abs(elat1 - blat1)
#    dlon1 = abs(elon1 - blon1)
#
#    nsegment = points[ix + 1 if (ix + 1) < len(points) else 0]
#    blat2 = ROAD_LIST[nsegment[0]][S_BLAT]
#    blon2 = ROAD_LIST[nsegment[0]][S_BLON]
#    elat2 = ROAD_LIST[nsegment[0]][S_ELAT]
#    elon2 = ROAD_LIST[nsegment[0]][S_ELON]
#    dlat2 = abs(elat2 - blat2)
#    dlon2 = abs(elon2 - blon2)
#
#    if segment[0] == nsegment[0]:
#      # Great, we're measuring distance between two points on the same road
#      this_lat = (nsegment[1] - segment[1]) * dlat1
#      this_lon = (nsegment[1] - segment[1]) * dlon1
#      distance = math.sqrt(this_lat * this_lat + this_lon * this_lon)
#      distances.append(distance)
#    else:
#      # Sum the distance travelled on the two segments
#      this_lat = (1 - segment[1]) * dlat1
#      this_lon = (1 - segment[1]) * dlon1
#      distance1 = math.sqrt(this_lat * this_lat + this_lon * this_lon)
#
#      this_lat = nsegment[1] * dlat1
#      this_lon = nsegment[1] * dlon1
#      distance2 = math.sqrt(this_lat * this_lat + this_lon * this_lon)
#
#      distance = distance1 + distance2
#      distances.append(distance)
#
#  total_distance = sum(distances)
#  distance_travelled = sum(distances[:segment_ix]) + (segment_percent * distances[segment_ix])
#  return distance_travelled / total_distance
  
  ####
  # get_street_list generates a list of streets used by this route
  #
  # return is a list of street indices
  ####
  #def get_street_list(self):
  #  if len(self.segments) > 0:
  #    return set(segment.roadIx for segment in self.segments)
