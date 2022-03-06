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
  def describe(self, nodeDict):
    print("Name: " + self.name)
    print("Direction: " + self.dir)
    for point in self.points:
      print(f"{point.addr} at {nodeDict[point.node].lat}, {nodeDict[point.node].lon}")

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
  # edit helps the user edit or delete points in point list, or name and/or direction
  ####
  def edit(self, nodeDict):
    while True:
      print("n: Name: " + self.name)
      print("d: Direction: " + self.dir)
      for pointIx, point in enumerate(self.points):
        print(f"{pointIx+1}: {point.addr} at {nodeDict[point.node].lat}, {nodeDict[point.node].lon}")
      action = CvtdUtil.input_int(f"What do you want to edit or delete? Enter 'q' when done: ", 1, len(self.points), validAnswers=['q', 'n', 'd'])
      if type(action) is int:
        realPointIx = action - 1
        pointAction = CvtdUtil.input_int(f"Choose one of the following: (1) edit addr, (2) edit node, (3) delete point: ", 1, 3)
        if pointAction == 1:
          # If we have more than one point, increasing/decreasing is defined and we can maintain the constraint
          # Else, we just need to set neAddr to the current
          if len(self.points) > 1:
            if self.increasing:
              minAddr = self.points[realPointIx - 1].addr + 1 if realPointIx > 0 else None
              maxAddr = self.points[realPointIx + 1].addr - 1 if realPointIx < (len(self.points) - 1) else None
            else:
              maxAddr = self.points[realPointIx - 1].addr - 1 if realPointIx > 0 else None
              minAddr = self.points[realPointIx + 1].addr + 1 if realPointIx < (len(self.points) - 1) else None
          else:
            minAddr = None
            maxAddr = None
          self.points[realPointIx].addr = CvtdUtil.input_int(f"Enter a new address (min {minAddr}, max {maxAddr}): ", minAddr, maxAddr)
        elif pointAction == 2:
          print("Not Implemented Error. Sorry")
        elif pointAction == 3:
          del self.points[realPointIx]
      elif action == 'n':
        self.name = input("Enter name for this road: ")
      elif action == 'd':
        self.dir = input(f"Enter a direction for {self.name} ('N/S', 'E/W', or other'): ")
      else:
        break
  
  ####
  # compute_proj_ratio returns percent from begin or end, on the segment with least error
  #
  # self is the containing CvtdMap
  # lat is the latitude of the point to try to find a street for
  # lon is the longitude of the point to try to find a street for
  # nodeDict is the node dictionary that nodes lie on
  # 
  # return[0] is index of the point that begins this segment within the street, [0 to len(self.points) - 2]
  # return[1] is projection ratio, where 0 is the beginning and 1 is the end of the segment
  # return[2] is scalar error, can be passed to CvtdUtil.coord_to_ft() to get an approximate error in feet
  ####
  def compute_proj_ratio(self, lat, lon, nodeDict):
    min_point_ix = 0
    min_proj_ratio = 0
    min_pos_to_proj = 0x7FFFFFFF
    
    for point_ix, point in enumerate(self.points[:-1]):
      blon = nodeDict[point.node].lon
      blat = nodeDict[point.node].lat
      elon = nodeDict[self.points[point_ix + 1].node].lon
      elat = nodeDict[self.points[point_ix + 1].node].lat
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
  # nodeDict is the node dictionary that nodes lie on
  #
  # return[0] is the best address to represent the point
  # return[1] is the error in feet
  ####
  def compute_addr(self, lat, lon, nodeDict):
    point_ix, proj_ratio, error = self.compute_proj_ratio(lat, lon, nodeDict)

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
  # nodeDict is the list or dictionary referred to by the road
  #
  # return is the best address for that node, or None if operation failed
  ####
  def estimate_addr(self, node, nodeDict):
    # Compute proj ratio so that we can estimate using the closest segment
    point_ix, proj_ratio, error = self.compute_proj_ratio(node.lat, node.lon, nodeDict)
    try:
      if proj_ratio < 0:
        # The node lies beyond the first point
        startNode = nodeDict[self.points[0].node]
        startAddr = self.points[0].addr
        refNode = nodeDict[self.points[1].node]
        refAddr = self.points[1].addr
      elif proj_ratio > 1:
        # The node lies beyond the last point
        startNode = nodeDict[self.points[-2].node]
        refNode = nodeDict[self.points[-1].node]
        startAddr = self.points[-2].addr
        refAddr = self.points[-1].addr
      else:
        # The node lies in between two points
        startNode = nodeDict[self.points[point_ix].node]
        refNode = nodeDict[self.points[point_ix+1].node]
        startAddr = self.points[point_ix].addr
        refAddr = self.points[point_ix+1].addr

      try:
        addrPerLat = (refAddr - startAddr) / (refNode.lat - startNode.lat)
      except ZeroDivisionError:
        addrPerLat = 0
      try:
        addrPerLon = (refAddr - startAddr) / (refNode.lon - startNode.lon)
      except ZeroDivisionError:
        addrPerLon = 0
  
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

  ####
  # insert tries to insert a point into the appropriate location based on address
  #
  # p is the point to insert
  ####
  def insert(self, p):
    if len(self.points) > 1:
      inc = self.increasing()
      for point_ix, point in enumerate(self.points):
        # If the address is between nextPoint.addr and point.addr
        if (inc and (point.addr > p.addr)) or (not inc and (point.addr < p.addr)):
          # Insert at the first location where the next point is greater than me if increasing
          # Insert at the first location where the next point is less than me if decreasing
          self.points.insert(point_ix, p)
          return
    elif len(self.points) == 1:
      if p.addr < self.points[0].addr:
        self.points.insert(0, p)
        return
    self.points.append(p)

  ####
  # extendable checks to see if another road can be tacked onto this one, by comparing lat and lon of endpoints
  #
  # otherRoad is the other road to attempt to tack on
  #
  # returns True if extendable, else False
  ####
  def extendable(self, otherRoad):
    # If one road is fully contained within the other, the answer is no
    if all([x in [p.node for p in otherRoad.points] for x in [self.points[0].node, self.points[-1].node]]):
      return False
    if all([x in [p.node for p in self.points] for x in [otherRoad.points[0].node, otherRoad.points[-1].node]]):
      return False

    if self.points[0].node == otherRoad.points[0].node:
      # self.points = list(reversed(otherRoad.points[1:])) + self.points
      return True
    elif self.points[0].node == otherRoad.points[-1].node:
      # self.points = otherRoad.points[:-1] + self.points
      return True
    elif self.points[-1].node == otherRoad.points[0].node:
      # self.points = self.points + otherRoad.points[1:]
      return True
    elif self.points[-1].node == otherRoad.points[-1].node:
      # self.points = self.points + list(reversed(otherRoad.points[:-1]))
      return True
    return False

  ####
  # compare_road returns the relationship between this road and otherRoad, if any
  #
  # nodeDict is the node dictionary for this road
  # otherRoad is the other road to compare to
  # otherNodeDict is the node dictionary for the other road
  #
  # returns a code that identifies the relationship
  #  -1 means there is no correlation
  #  0 means that they are identical
  #  1 means that otherRoad is fully contained in this road (otherRoad has no new information)
  #  2 means that this road is fully contained in otherRoad (otherRoad has new information on at least one side)
  #  3 means that there is at least one intersection, but no matching nodes on the edges
  #  4 means that there is overlap (one end of one road exactly matches on end of the other road)
  ####
  def compare_road(self, nodeDict, otherRoad, otherNodeDict):
    match = None
    otherIncrementer = 1

    for nodeIx, nodeNo in enumerate([p.node for p in self.points]):
      try:
        node = nodeDict[nodeNo]
      except KeyError:
        # It's possible that nodes will be in self.points that are not in nodeDict
        # But it *should* be guaranteed that they will be in otherNodeDict
        node = otherNodeDict[nodeNo]
      matchFoundThisNode = False
      for oNodeIx, oNodeNo in enumerate([p.node for p in otherRoad.points]):
        oNode = otherNodeDict[oNodeNo]

        # Compare these two nodes. If we found a match, try to pursue it
        if node.compare_node(oNode):
          match = [nodeIx, oNodeIx, 1]
          if oNodeIx == len(otherRoad.points) - 1:
            otherIncrementer = -1
          matchFoundThisNode = True
          break
      if matchFoundThisNode:
        break
    
    # If we never found a match, return -1
    if match is None:
      return -1

    # We found a match, follow it to the end of either road or until it's not a match
    while True:
      nodeIx = nodeIx + 1
      oNodeIx = oNodeIx + otherIncrementer
      if nodeIx == len(self.points):
        # We reached the end of this road. Did we reach the end of the other road?
        if oNodeIx == len(otherRoad.points) or oNodeIx == -1:
          # We did. Was there anything else more interesting on the other road?
          if match[0] == match[1] and match[0] == 0:
            return 0
          elif match[1] != 0:
            return 4
          else:
            return 1
        else:
          # We didn't reach the end of the other road, but we did reach the end of this road
          if match[0] != 0:
            return 4
          else:
            return 2
      else:
        # We didn't reach the end of this road. Did we reach the end of the other road?
        if oNodeIx == len(otherRoad.points) or oNodeIx == -1:
          # We did. Did their match begin at 0? If not, they have something new. Else they are contained
          if match[1] != 0:
            return 4
          else:
            return 1
        else:
          # We didn't reach the end of either road. Do we still have a match?
          nodeNo = self.points[nodeIx].node
          oNodeNo = otherRoad.points[oNodeIx].node
          try:
            node = nodeDict[nodeNo]
          except KeyError:
            # See note above
            node = otherNodeDict[nodeNo]
          oNode = otherNodeDict[oNodeNo]
          if node.compare_node(oNode):
            # The match continues, increment match[2]
            match[2] = match[2] + 1
          else:
            # The match has been broken. Unless we have the possibility of a 1-node junction, we get an intersection
            if match[0] == 0 and (match[1] == 0 or match[1] == (len(otherRoad.points) - 1)) and match[2] == 1:
              return 4
            else:
              return 3
            
