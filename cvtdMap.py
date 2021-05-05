import datetime
import math
import os

from cvtdContainedRoadPoint import ContainedRoadPoint
from cvtdNode import CvtdNode
from cvtdRoad import CvtdRoad
from cvtdRoadPoint import CvtdRoadPoint
from cvtdUtil import CvtdUtil

####
# A class containing a node list, road list, and other variables
#
# nodeList -> Array of Node objects
# roadList -> Array of Road objects
# routelist -> Array of Route objects
####
class CvtdMap:
  def __init__(self):
    self.nodeList = []
    self.roadList = []
    self.routeList = []

  ####
  # validate calls validate() on every road and route, printing results to the screen
  ####
  def validate(self):
    invalidRoads = []
    for road in self.roadList:
      if not road.validate():
        invalidRoads.append(road)

    if len(invalidRoads) > 0:
      print(f"The following {len(invalidRoads)} roads are invalid: ")
      for invalid in invalidRoads:
        invalid.describe()

    invalidRoutes = []
    for route in self.routeList:
      if not route.validate():
        invalidRoutes.append(route)

    if len(invalidRoutes) > 0:
      print(f"The following {len(invalidRoutes)} routes are invalid: ")
      for invalid in invalidRoutes:
        invalid.describe()

    if len(invalidRoads) == 0 and len(invalidRoutes) == 0:
      print("You got a perfect score!")

  ####
  # compute_proj_ratio finds the street that the given node is most likely on
  #
  # self is the containing CvtdMap
  # lat is the latitude of the point to try to find a street for
  # lon is the longitude of the point to try to find a street for
  # valid_streets is an array of street indexes to consider (if None, all streets are considered)
  # 
  # return[0] is index of the street that point most likely lies on
  # return[1] is index of the segment within the street
  # return[2] is projection ratio, where 0 is the beginning and 1 is the end of the segment
  # return[3] is scalar error, can be passed to CvtdUtil.coord_to_ft() to get an approximate error in feet
  ####
  def compute_proj_ratio(self, lat, lon, valid_streets):
    min_street_ix = -1
    min_point_ix = -1
    min_proj_ratio = 0
    min_pos_to_proj = 0x7FFFFFFF

    for street_ix, street in enumerate(self.roadList):
      if valid_streets is None or street_ix in valid_streets:
        point_ix, proj_ratio, pos_to_proj = street.compute_proj_ratio(lat, lon, self.nodeList)

        if pos_to_proj < min_pos_to_proj:
          min_street_ix = street_ix
          min_point_ix = point_ix
          min_proj_ratio = proj_ratio
          min_pos_to_proj = pos_to_proj

    return min_street_ix, min_point_ix, min_proj_ratio, min_pos_to_proj

  ####
  # compute_addr attempts to compute an address of a given point
  # lat is the latitude of the point to compute
  # lon is the longitude of the point to compute
  # valid_streets is an array of street indexes to consider (if None, all streets are considered)
  #
  # return[0] is the index of the street that the address lies on
  # return[1] is the integer representation of the best address to represent the point
  # return[2] is the error in feet
  ####
  def compute_addr(self, lat, lon, valid_streets):
    ix, seg_ix, proj_ratio, error = self.compute_proj_ratio(lat, lon, valid_streets)

    if ix != -1:
      vaddr_begin = self.roadList[ix].points[seg_ix].addr
      vaddr_end = self.roadList[ix].points[seg_ix+1].addr

      address = round(proj_ratio * (vaddr_end - vaddr_begin) + vaddr_begin)
    else:
      address = 0

    return ix, address, CvtdUtil.coord_to_ft(error)

  ####
  # compute_addr_repr attempts to compute an address of a given point
  # lat is the latitude of the point to compute
  # lon is the longitude of the point to compute
  # valid_streets is an array of street indexes to consider (if None, all streets are considered)
  #
  # return[0] is the index of the street that the address lies on
  # return[1] is the string representation best address to represent the point
  # return[2] is the error in feet
  ####
  def compute_addr_repr(self, lat, lon, valid_streets):
    ix, address, error = self.compute_addr(lat, lon, valid_streets)
    if ix != -1:
      addrRepr = CvtdUtil.addr_repr(address, self.roadList[ix].dir, self.roadList[ix].name)
    else:
      addrRepr = "N/A"

    return ix, addrRepr, error

  ####
  # get_node_usage returns a list of road points using a given node index
  #
  # node_ix is the index into NODE_LIST to search for
  #
  # return[0] is a list of ContainedRoadPoints
  ####
  def get_node_usage(self, node_ix):
    plist = []
    for ix, road in enumerate(self.roadList):
      for segment in road.points:
        if segment.node == node_ix:
          plist.append(ContainedRoadPoint(segment.addr, ix))
    return plist
    
  ####
  # generate_dlist generates a list of distances from each node to the given point
  #
  # lat is the latitude of the point to which distance will be calculated
  # lon is the longitude of the point to which distance will be calculated
  #
  # return[0] is the list, an unsorted list of doubles that aligns with NODE_LIST
  ####
  def generate_dlist(self, lat, lon):
    return [math.sqrt(((lat - a.lat) * (lat - a.lat)) + ((lon - a.lon) * (lon - a.lon))) for a in self.nodeList]
    
  ####
  # search_street_by_name is a subroutine that returns streets that match a given name
  #
  # name is the portion of the name to search streets for
  # printList is whether to print matches to the screen
  #
  # return[0] is an array of matches
  #  return[i][0] is road index
  #  return[i][1] is negative terminus of road
  #  return[i][2] is positive terminus of road
  ####
  def search_street_by_name(self, name, printList):
    matches = []
    for ix, road in enumerate(self.roadList):
      if name in road.name:
        negterm, posterm = road.get_endpoints()
        if negterm and posterm:
          matches.append([ix, negterm, posterm])
    
    if printList:
      print(f"{len(matches)} matches were found.")
      for i, match in enumerate(matches):
        name = self.roadList[match[0]].name
        dir = self.roadList[match[0]].dir
        print(f"({i+1}) {name} from {CvtdUtil.addr_dir(match[1], dir)} to {CvtdUtil.addr_dir(match[2], dir)}")
    return matches

  ####
  # find_intersecting_roads returns a list of intersecting roads with the given road, on all segments
  #
  # road_ix is an index into ROAD_LIST
  # tol is a tolerance value in feet, if a point lies within tol of an intersection, consider it an intersection
  #
  # return is a list of intersecting roads
  #  return[i][0] is a containedRoadPoint for original road
  #  return[i][1] is a containedRoadPoint for intersecting road
  ####
  def find_intersecting_roads(self, road_ix, tol):
    intersections = []
    
    # Find roads that intersect with each segment individually
    road = self.roadList[road_ix]
    for point_ix, point in enumerate(road.points[:-1]):
      n1s = self.nodeList[point.node]
      n1e = self.nodeList[road.points[point_ix + 1].node]
      
      # Loop through all roads to see if they intersect with this segment
      for check_ix, check_road in enumerate(self.roadList):
        # Don't check to see if a road intersects with itself
        if check_ix != road_ix:
          for check_point_ix, check_point in enumerate(check_road.points[:-1]):
            n2s = self.nodeList[check_point.node]
            n2e = self.nodeList[check_road.points[check_point_ix + 1].node]
            
            cross = CvtdUtil.get_line_intersection(n1s, n1e, n2s, n2e)
            if cross:
              addr1 = self.compute_addr(cross[0], cross[1], [road_ix])[1]
              addr2 = self.compute_addr(cross[0], cross[1], [check_ix])[1]
              p1 = ContainedRoadPoint(addr1, road_ix)
              p2 = ContainedRoadPoint(addr2, check_ix)
              intersections.append([p1, p2])
    return intersections
  
  ####
  # sort_filter_intersections sorts intersections positive to negative along some axis, and filters
  #
  # intersections is the result of a find_intersecting_roads() call
  # forceDirection is 1, 0 or None
  #  if forceDirection is 1, intersections will be keep only if the original road address is greater than segBeginAddr
  #  if forceDirection is 0, intersections will be keep only if the original road address is less than segBeginAddr
  #  if forceDirection is None, no filtering will be done
  # segBeginAddr is used when forceDirection is 1 or 0, as described above
  ####
  def sort_filter_intersections(self, intersections, forceDirection, segBeginAddr):
    if forceDirection == 1:
      intersections = [i for i in intersections if i[0].addr > segBeginAddr]
    elif forceDirection == 0:
      intersections = [i for i in intersections if i[0].addr < segBeginAddr]
    intersections.sort(key=lambda i: i[0].addr)
    return intersections

  ####
  # read_roads reads a Python file and loads the results into NODE_LIST and ROAD_LIST
  #
  # filename is the file to read from (typically roads.txt)
  ####
  def read_roads(self, filename):
    self.nodeList = []
    self.roadList = []
  
    editor = ""
    this_road = CvtdRoad()
    try:
      with open(filename, 'r') as f:
        for road in f:
          if road.strip() == "NODE_LIST = [":
            editor = "NODE_LIST"
          elif road.strip() == "ROAD_LIST = [":
            editor = "ROAD_LIST"
          elif editor == "NODE_LIST" and len(road.strip().split(',')) == 3:
            lat = float(road.split(',')[0].strip().replace('[',''))
            lon = float(road.split(',')[1].strip().replace(']',''))
            self.nodeList.append(CvtdNode(lat, lon))
          elif editor == "ROAD_LIST" and len(road.strip().split('",')) == 3:
            this_road = CvtdRoad()
            this_road.name = road.split('",')[0].replace('[','').replace('"','').strip()
            this_road.dir = road.split('",')[1].replace('"','').strip()
            points = road.split('",')[2].split('], [')
            points = [p.replace('[','').replace(']','').replace(',\n','').strip() for p in points]
            this_road.points = [CvtdRoadPoint(int(node), int(addr)) for node, addr in [x.split(', ') for x in points]]
            self.roadList.append(this_road)
        print("Read successful, read {} nodes and {} roads".format(len(self.nodeList), len(self.roadList)))
    except FileNotFoundError:
      print("Error: File \"{}\" does not exist".format(filename))

  ####
  # write_roads writes the current NODE_LIST and ROAD_LIST to a Python file
  #  write_roads also backs up the current roads.txt file if it exists, to roads_200614_082431
  #
  # filename is the name of the output file (default roads.txt)
  ####
  def write_roads(self, filename):
    if filename == "roads.txt":
      curtime = datetime.datetime.now()
      bkp_name = datetime.date.strftime(curtime, 'roads_%Y%m%d_%H%M%S.txt')
      try:
        os.rename(filename, bkp_name)
        print(f"Renamed current roads.txt file to {bkp_name}")
      except FileNotFoundError:
        pass

    with open(filename, 'w') as f:
      f.write("NODE_LIST = [\n")
      for node in self.nodeList:
        f.write("    [{}, {}],\n".format(node.lat, node.lon))
      f.write("]\n\n")

      f.write("ROAD_LIST = [\n")
      for road in self.roadList:
        s1 = f'    ["{road.name}", "{road.dir}", ['
        s2 = ', '.join(["[" + str(p.node) + ", " + str(p.addr) + "]" for p in road.points])
        s3 = ']],\n'
        f.write(s1 + s2 + s3)
      print("Write successful")

  ####
  # add_street adds a street to the map, validating it first
  #
  # street is the CvtdRoad to add
  #
  # return[0] is the results of street.validate()
  ####
  def add_street(self, street):
    valid = street.validate()
    if valid:
      self.roadList.append(street)
    return valid
  
  ####
  # add_street_with_nodes adds a street to the map, copying nodes from an existing node list and merging them into this node list
  ####
  def add_street_with_nodes(self, street, fromNodeList):
    if street.validate():
      for point in street.points:
        # Search in the current node list for a node almost equal to this node
        found = False
        for nodeIx, node in enumerate(self.nodeList):
          if (abs(node.lat - fromNodeList[point.node].lat) < 0.000001) and (abs(node.lon - fromNodeList[point.node].lon) < 0.000001):
            point.node = nodeIx
            break
        if not found:
          self.nodeList.append(fromNodeList[point.node])
      self.add_street(street)

  ####
  # bnum_to_route gets the route that has this bus number
  #
  # bnum is the bus number to look up
  #
  # return is a CvtdRoute
  ####
  def bnum_to_route(self, bnum):
    for route in self.routeList:
      if bnum in [bus.busNumber for bus in route.buses]:
        return route

  ####
  # bnum_to_street_list gets a set of indices into self.roadList that this route uses
  #
  # bnum is the bus number to look up
  #
  # return is a set of integers that index into self.roadList, or {} if bus number not found
  ####
  def bnum_to_street_list(self, bnum):
    route = self.bnum_to_route(bnum)
    try:
      return route.get_street_list()
    except AttributeError:
      return None

