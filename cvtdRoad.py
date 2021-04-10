from cvtdUtil import CvtdUtil

import math

####
# A class representing a road, consisting of multiple segments
#
# name -> Name of road
# dir -> Direction of road as a string, most likely "N/S" or "E/W"
# points -> Array of RoadPoint objects
####
class CvtdRoad:
  def __init__(self):
    self.name = ""
    self.dir = ""
    self.points = []

  ####
  # describe prints information about the road
  ####
  def describe(self, nodeList):
    print("Name: " + self.name)
    print("Direction: " + self.dir)
    for point in self.points:
      print(f"{point.addr} at {nodeList[point.node].lat}, {nodeList[point.node].lon}")

  ####
  # validate makes sure that addresses on a road are monotonically increasing or decreasing
  ####
  def validate(self):
    addresses = [p.addr for p in self.points]
    
    # Calculates the difference between each element
    diff = [y - x for x, y in zip(addresses, addresses[1:])]
    
    # Either all differences must be positive, or they all must be negative
    valid = all(x > 0 for x in diff) or all(x < 0 for x in diff)
    return valid
  
  ####
  # compute_proj_ratio returns percent from begin or end, on the segment with least error
  #
  # self is the containing CvtdMap
  # lat is the latitude of the point to try to find a street for
  # lon is the longitude of the point to try to find a street for
  # nodeList is the node list that nodes lie on
  # 
  # return[0] is index of the point that begins this segment within the street, [0 to len(self.points) - 2]
  # return[1] is projection ratio, where 0 is the beginning and 1 is the end of the segment
  # return[2] is scalar error, can be passed to CvtdUtil.coord_to_ft() to get an approximate error in feet
  ####
  def compute_proj_ratio(self, lat, lon, nodeList):
    min_point_ix = 0
    min_proj_ratio = 0
    min_pos_to_proj = 0x7FFFFFFF
    
    for point_ix, point in enumerate(self.points[:-1]):
      blon = nodeList[point.node].lon
      blat = nodeList[point.node].lat
      elon = nodeList[self.points[point_ix + 1].node].lon
      elat = nodeList[self.points[point_ix + 1].node].lat
      street_sc, pos_sc, projection_sc, begin_or_end = CvtdUtil.sub_proj_ratio(lat, lon, blat, blon, elat, elon)

      if projection_sc != 0.0:
        proj_sc_fixed = min(projection_sc, street_sc)
        try:
          pos_to_proj = math.sqrt((pos_sc * pos_sc) - (proj_sc_fixed * proj_sc_fixed))
        except ValueError:
          pos_to_proj = 0

        if pos_to_proj < min_pos_to_proj:
          min_point_ix = point_ix
          min_proj_ratio = projection_sc / street_sc
          min_pos_to_proj = pos_to_proj

          if begin_or_end == 0:
            min_proj_ratio = 1 - min_proj_ratio
      else:
        print(f"Error [compute_proj_ratio] on road called {self.name}: two adjacent points with same node")
      
    return min_point_ix, min_proj_ratio, min_pos_to_proj
    
  ####
  # compute_addr attempts to project a given point onto this street
  # lat is the latitude of the point to compute
  # lon is the longitude of the point to compute
  # nodeList is the node list that nodes lie on
  #
  # return[0] is the best address to represent the point
  # return[1] is the error in feet
  ####
  def compute_addr(self, lat, lon, nodeList):
    point_ix, proj_ratio, error = self.compute_proj_ratio(lat, lon, nodeList)

    vaddr_begin = self.points[point_ix].addr
    vaddr_end = self.points[point_ix+1].addr

    address = round(proj_ratio * (vaddr_end - vaddr_begin) + vaddr_begin)
    addrRepr = CvtdUtil.addr_repr(address, self.dir, self.name)

    return addrRepr, CvtdUtil.coord_to_ft(error)
  
  ####
  # get_endpoints finds the minimum and maximum addresses on this road
  # 
  # return[0] is the minimum address
  # return[1] is the maximum address
  ####
  def get_endpoints(self):
    negterm = None
    posterm = None
    for point in self.points:
      if negterm == None or point.addr < negterm:
        negterm = point.addr
      if posterm == None or point.addr > posterm:
        posterm = point.addr
    return [negterm, posterm]

  ####
  # Given a node, estimate an address for that node (requires at least 2 addresses already defined)
  #
  # node is a CvtdNode representing the point to interpolate to
  # nodeList is the list or dictionary referred to by the road
  #
  # return is the best address for that node, or None if operation failed
  ####
  def estimate_addr(self, node, nodeList):
    # Compute proj ratio so that we can estimate using the closest segment
    point_ix, proj_ratio, error = self.compute_proj_ratio(node.lat, node.lon, nodeList)
    try:
      if proj_ratio < 0:
        # The node lies beyond the first point
        startNode = nodeList[self.points[0].node]
        startAddr = self.points[0].addr
        refNode = nodeList[self.points[1].node]
        refAddr = self.points[1].addr
      elif proj_ratio > 1:
        # The node lies beyond the last point
        startNode = nodeList[self.points[-2].node]
        refNode = nodeList[self.points[-1].node]
        startAddr = self.points[-2].addr
        refAddr = self.points[-1].addr
      else:
        # The node lies in between two points
        startNode = nodeList[self.points[point_ix].node]
        refNode = nodeList[self.points[point_ix+1].node]
        startAddr = self.points[point_ix].addr
        refAddr = self.points[point_ix+1].addr

      addrPerLat = (refAddr - startAddr) / (refNode.lat - startNode.lat)
      addrPerLon = (refAddr - startAddr) / (refNode.lon - startNode.lon)
      latAddrTot = addrPerLat * (node.lat-startNode.lat)
      lonAddrTot = addrPerLon * (node.lon-startNode.lon)
      latDiff = refNode.lat - startNode.lat
      lonDiff = refNode.lon - startNode.lon
      latCmp = latDiff/(latDiff + lonDiff)
      lonCmp = lonDiff/(latDiff + lonDiff)
      latAddrInt = startAddr + latAddrTot
      lonAddrInt = startAddr + lonAddrTot
      return (latAddrInt * latCmp) + (lonAddrInt * lonCmp)
    except (TypeError, IndexError):
      return None
  
  ####
  # Checks to see if a road's addresses are increasing or decreasing
  #
  # return True if increasing, False if decreasing, None if invalid
  ####
  def increasing(self):
    if len(self.points) < 2:
      return None
    return self.points[-1].addr > self.points[0].addr
