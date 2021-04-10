import datetime
import math
import os

from cvtdContainedRoadPoint import ContainedRoadPoint
from cvtdMap import CvtdMap
from cvtdNode import CvtdNode
from cvtdRoad import CvtdRoad
from cvtdRoadPoint import CvtdRoadPoint
from cvtdRoute import CvtdRoute
from cvtdRouteSegment import CvtdRouteSegment
from cvtdUtil import CvtdUtil

# TO DO:
#  Test roadTool!
#  Update cvtdapp.py
#  Change roads.txt so that it takes less space and is not a text file, and record routes
#  Write OSM reader
#  Execute OSM reader to get a better roads.txt file
#  Store bus locations to disk

# Moving forward:
# 
# struct Node: latitude, longitude
#
# struct RoadSegment: loc (Node), addr (int), name (str or null), dir (str)
#
# class Road:
#  list of RoadSegments
#  method: proj_ratio_to_addr(seg_ix, proj_ratio)
#  method: addr_to_proj_ratio(seg_ix, addr)
#  method: seg_length(seg_ix)
#
# struct RouteSegment: road (index)
# 
# class Route: name (str), xmlname (str), 
#  list of RouteSegments
#  
# class City:
#  list of Nodes
#  method: node_in_city(node)
#
# class Map:
#  list of Roads
#  list of Routes
#  list of Cities
#  method: 
#
# Roadtool Main:
#  instantiate Map from file
#  allow adding, editing, deleting Roads (resolve issues with Routes)
#  allow adding, editing, deleting Routes
#  allow adding, editing, deleting Cities
#  allow instantiation of a second Map from OSM
#

# NODE_LIST is just a list of 2-element arrays
NLAT = 0
NLON = 1

# ROAD_LIST is an array of roads, each of which has a name, direction, and list of at list two segments
RNAME = 0
RDIR = 1
RSEGS = 2

# RSEGS points to a list of segments, each of which is an array of two integers
SNODE = 0
SADDR = 1

SEGNODE = 0
SEGADDR = 1
SEGNAME = 2
SEGDIR = 3

# ROUTE_LIST is an array of routes, each of which is a 2-element array
ROUTENAME = 0    # Displayed name of the route (routes with same name will be combined)
ROUTEXMLNAME = 1  # Name of the route in an XML file
ROUTESEGS = 2    # Array of route segments
ROUTESTOPS = 3    # Array of stops on route
ROUTEFIXS = 4    # Times at which the route should depart stop with index 0, [] for timefree routes
# The second element is an array of at least 2 segments
RSEGROAD = 0
RSEGBSEG = 1
RSEGBADDR = 2
RSEGESEG = 3
RSEGEADDR = 4
# The third element is an array of stops
RSTOPROAD = 0
RSTOPADDR = 1
RSTOPNAME = 2
RSTOPNICKNAME = 3

# CITY_LIST is just an array of arrays of nodes
CNODELIST = 0

NODE_LIST = []
ROAD_LIST = []
ROUTE_LIST = []
CITY_LIST = []

####
# parse_gps attempts to parse a string into separate lat and lon portions
#
# return[0] indicates whether the parsing was ultimately successful
# return[1] indicates the user-provided latitute
# return[2] indicates the user-provided longitude
####
def parse_gps():
  keepTrying = True
  valid = False
  while keepTrying:
    gps = input("Enter GPS location (lat lon): ").strip().replace('(','').replace(')','').replace(',','')
    parts = [p.strip() for p in gps.split()]
    lat, lon = 0.0, 0.0
    if len(parts) == 2:
      try:
        lat, lon = [float(p) for p in parts]
        keepTrying = False
        valid = True
      except ValueError:
        pass
    if keepTrying:
      keepTrying = input("I'm sorry, I couldn't understand that. Keep trying (y/n)? ").lower() == 'y'
    
  return valid, lat, lon

####
# choose_gps returns a GPS coordinate, attempting the help the user choose an existing surrounding node
#
# return[0] is NODE_LIST index of the chosen node (len(NODE_LIST) if new)
#  or None if the user did not choose a node but wants to try again
#  or False if the user is aborting the operation
# return[1] is the latitude value
# return[2] is the longitude value
####
def choose_gps(map):
  valid, lat, lon = parse_gps()
  if not valid:
    return False
  node_ix = len(map.nodeList)
  dlist = map.generate_dlist(lat, lon)
  dlist_sorted = sorted(dlist)
  node_count = sum([CvtdUtil.coord_to_ft(y) < 150 for y in dlist])
  if node_count > 0:
    print(f"The following {node_count} nodes already exist close to the location you entered:")
    for i in range(node_count):
      dlist_ix = dlist.index(dlist_sorted[i])
      print(f"{i+1}: {map.nodeList[dlist_ix].lat}, {map.nodeList[dlist_ix].lon} ({CvtdUtil.coord_to_ft(dlist_sorted[i])} feet)")
    usenode = input("Use instead any of these nodes? Enter 'n' or number: ")
    try:
      usenode = int(usenode)
      if 1 <= usenode <= node_count:
        plist = map.get_node_usage(dlist_ix)
        if len(plist) > 0:
          print("The following roads use this node: ")
          for point in plist:
            print(p.addr_repr(map.roadList))
          okay = input("Okay (y/n): ")
          if okay.lower() != 'y':
            return None
        else:
          lat = map.nodeList[dlist_ix].lat
          lon = map.nodeList[dlist_ix].lon
          node_ix = dlist_ix
    except ValueError:
      # node_ix, lat and lot already have their desired values
      pass
  return node_ix, lat, lon

####
# define_road_details creates a road and defines its name and direction
#
# return the road, with no points defined
####
def define_road_details():
  this_road = CvtdRoad()
  this_road.name = input('Street name: ')
  this_road.dir = input('Direction (most likely "N/S" or "E/W"): ')
  return this_road

####
# define_street queries the user to define a road's point list
#
# map is the CvtdMap to use
# this_road is the road to define the points for
# 
# return the road, or None if aborted
####
def define_road_points(map, this_road):
  more_points = "Y"
  while more_points.lower() == "y":
    gps = None
    while gps is None:
      gps = choose_gps(map)
      
    if gps is not False:
      address = input("Enter street address: ")
      try:
        address = int(address)
        
        # Now we need to make sure that this road will be "valid" -- that each address is either higher or lower than previous one
        try:
          if ((address - this_road.points[-1].addr) * (this_road.points[1].addr - this_road.points[0].addr)) < 0:
            increasing = this_road.points[1].addr > this_road.points[0].addr
            print(f"Addresses on this road are {'increasing' if increasing else 'decreasing'}, so this address must be {'greater' if increasing else 'less'} than {this_road.points[-1].addr}")
            more_points = input("Try again (y/n):")
            if more_points.lower() == 'y':
              continue
            else:
              return
        except IndexError:
          # Road hasn't yet established a direction
          pass
        
        # Add the node to the nodeList if it hasn't been added yet
        if gps[0] == len(map.nodeList):
          map.nodeList.append(CvtdNode(gps[1], gps[2]))
        
        point = CvtdRoadPoint(gps[0], address)
        this_road.points.append(point)
        print(f"Adding segment #{len(this_road.points)}: {CvtdUtil.addr_repr(address, this_road.dir, this_road.name)} at gps {gps[1]}, {gps[2]}")
        more_points = input("Add more points to road (y/n): ")
      except ValueError:
        more_points = input(f"Error: \"{address}\" could not be converted to an integer. Try again (y/n):")
        if more_points.lower() != 'y':
          return
    else:
      return
  return this_road

####
# new_street adds a road to the map.roadList, prompting for a list of GPS points, and name, direction, & address for each point
####
def new_street(map):
  this_road = define_road_details()
  this_road = define_road_points(map, this_road)
  if this_road is not None and len(this_road.points) > 1:
    if map.add_street(this_road):
      print(f"Adding road with {len(this_road.points)} points to road list")
    else:
      print("Error: The road could not be added.")
  else:
    print("No road was added.")
    
####
# search_streets directs the user to either search by name of GPS coordinate
####
def edit_delete_street(map, ix):
  print("Do you want to: ")
  print("(1) Edit this street's details")
  print("(2) Edit this street's point list")
  print("(3) Delete this street")
  print("(4) Return to main menu")
  action = input(">>> ")
  if action==1:
    new_road = define_road_details()
    new_road.points = map.roadList[ix].points
    map.roadList[ix] = new_road
  elif action==2:
    new_road = define_road_points(map, map.roadList[ix])
    if new_road is not None:
      map.roadList[ix] = new_road
  elif action==3:
    del map.roadList[ix]
    print(f"Road deleted. There are now {len(map.roadList)} roads")

####
# search_streets directs the user to either search by name of GPS coordinate
####
def search_streets(map):
  if len(map.roadList) == 0:
    print("Error: No streets currently exist.")
    return
  ix = -1
  stype = input("Search by (1) name or by (2) GPS coordinate? ")
  if stype == '1':
    name = input("Enter a portion of the street name: ")
    matches = map.search_street_by_name(name, True)
    if len(matches) > 1:
      try:
        whichMatch = int(input(f"Which match did you mean (1-{len(matches)}) or (n)o? "))-1
        if 0 <= whichMatch < len(matches):
          keepTrying = False
          ix = matches[whichMatch[0]]
        else:
          keepTrying = input("Invalid input. Try again (y/n)? ").lower() == 'y'
          whichMatch = -1
      except ValueError:
        keepTrying = input("Try again (y/n)? ").lower() == 'y'
    elif len(matches) == 1:
      whichMatch = 0
      ix = matches[whichMatch[0]]
      keepTrying = False
  elif stype == '2':
    valid, lat, lon = parse_gps()
    if valid:
      ix, addr, e = map.compute_addr_repr(lat, lon, None)
      print(f"{addr} (error {round(e, 3)})")

  if ix != -1:
    map.roadList[ix].describe()
    edit_delete_street(map, ix)

####
# new_route directs the user to create a new route and guides them through the process
####
def new_route(map):
  # Let them choose a starting point, like Wilder Rd, then list the names of the roads and the terminuses.
  # Let them choose one and an address.
  # Then let them choose an intersecting road to turn on, or return to the starting position
  this_route = CvtdRoute()
  
  # Figure out what street the route begins (and ends) on
  keepTrying = True
  whichMatch = -1
  while keepTrying:
    name = input("Enter street on route: ")
    matches = map.search_street_by_name(name, True)
    if len(matches) == 0:
      keepTrying = input("No matches were found, keep trying (y/n)? ").lower() == 'y'
    elif len(matches) > 1:
      try:
        whichMatch = int(input(f"Which match did you mean (1-{len(matches)}) or (n)o? "))-1
        if 0 <= whichMatch < len(matches):
          keepTrying = False
        else:
          keepTrying = input("Invalid input. Try again (y/n)? ").lower() == 'y'
          whichMatch = -1
      except ValueError:
        keepTrying = input("Try again (y/n)? ").lower() == 'y'
    else: 
      whichMatch = 0
      keepTrying = False
  
  # So that we know on which road the route begins
  try:
    beginRoadIx = matches[whichMatch][0]
    roadIx = beginRoadIx
  except IndexError:
    beginRoadIx = None
    roadIx = -1
  
  # Decide at what address to begin the route
  beginAddr = None
  if whichMatch != -1:
    road = map.roadList[beginRoadIx]
    beginRoad = road
    negterm = matches[whichMatch][1]
    posterm = matches[whichMatch][2]
    keepTrying = True
    while keepTrying:
      beginAddr = input(f"At what address does the route start? Choose a number from {negterm} to {posterm}: ")
      try:
        beginAddr = int(beginAddr)
        if negterm <= beginAddr <= posterm:
          keepTrying = False
        else:
          keepTrying = input("That address is invaild. Try again (y/n): ").lower() == 'y'
      except ValueError:
        keepTrying = input("I couldn't understand that. Try again (y/n): ").lower() == 'y'

  # If that was successful, choose intersecting roads until we return to this point
  if whichMatch != -1 and beginAddr is not None:
    segBeginAddr = beginAddr
    forceDirection = None  # 1 = forced positive address, 0 = forced negative address, None = no forcing
    
    # Now we know where the route is starting. 
    # Now, until the route is complete, let them choose from a list of intersecting roads
    # Or, let them turn around on the road they are currently on at a given address
    more_points = True
    while more_points:
      # Take an intersection, do a U-turn, or end the route if possible
      keepTrying = True
      nextRoadIx = None
      segEndAddr = None
      nextSegBeginAddr = None
      while keepTrying:
        print("Choose an intersection from the following options: ")
        intersections = map.find_intersecting_roads(roadIx, 150)
        intersections = map.sort_filter_intersections(intersections, forceDirection, segBeginAddr)
        for i, intersection in enumerate(intersections):
          print(f"{i+1}: Turn on {intersection[1].addr_repr(map.roadList)} at {intersection[0].addr_dir(map.roadList)}")
        print(f"{len(intersections)+1}: Execute a U-turn on {road.name}")
        if roadIx == beginRoadIx:
          print(f"{len(intersections)+2}: End route at {CvtdUtil.addr_dir(beginAddr, beginRoad.dir)}")
        intersection = input("Choose one of the above: ")
        try:
          intersection = int(intersection)
          if (0 < intersection <= len(intersections)):
            segEndAddr = intersections[intersection-1][0].addr
            nextRoadIx = intersections[intersection-1][1].roadIx
            nextSegBeginAddr = intersections[intersection-1][1].addr
            forceDirection = None
            keepTrying = False
          elif ((roadIx == beginRoadIx) and (intersection == (len(intersections)+2))):
            segEndAddr = beginAddr
            keepTrying = False
          elif (intersection == (len(intersections)+1)):
            negterm, posterm = road.get_endpoints()
            if forceDirection == 0:
              posterm = segBeginAddr
            elif forceDirection == 1:
              negterm = segBeginAddr
            turnAroundAddr = input(f"Enter address of U-turn ({negterm} to {posterm}): ")
            try:
              turnAroundAddr = int(turnAroundAddr)
              if negterm <= turnAroundAddr <= posterm and turnAroundAddr != segBeginAddr:
                segEndAddr = turnAroundAddr
                nextRoadIx = roadIx
                nextSegBeginAddr = turnAroundAddr
                
                # If we did a U-turn after going "up", we must next go down
                # If we did a U-turn after going "down", we must next go back up
                if turnAroundAddr > segBeginAddr:
                  forceDirection = 0
                else:
                  forceDirection = 1
                keepTrying = False
              else:
                keepTrying = input(f"{turnAroundAddr} is not within {negterm} and {posterm}. Keep trying (y/n): ").lower() == 'y'
            except ValueError:
              keepTrying = input("That didn't make sense. Keep trying (y/n): ").lower() == 'y'
          else:
            keepTrying = input("That didn't make sense. Keep trying (y/n): ").lower() == 'y'
        except ValueError:
          keepTrying = input("That didn't make sense. Keep trying (y/n): ").lower() == 'y'

      # If everything is valid, add this route segment
      if segEndAddr is not None:
        thisSeg = CvtdRouteSegment(roadIx, segBeginAddr, segEndAddr)
        this_route.segments.append(thisSeg)
      
        # Print info about this route so far
        print("Adding route: ")
        this_route.print_segments()
        
        # Check if the route definition is complete, or if we need more points
        if nextRoadIx is None:
          goAhead = input("Go ahead and add route (y/n): ").lower() == 'y'
          if goAhead:
            map.routeList.append(this_route)
            print(f"Route added. There are now {len(map.routeList)} routes.")
          more_points = False
        else:
          nextRoad = map.roadList[nextRoadIx]
          roadIx = nextRoadIx
          road = nextRoad
          print(f"\nNext segment of this route begins at {CvtdUtil.addr_repr(nextSegBeginAddr, nextRoad.dir, nextRoad.name)}")
          segBeginAddr = nextSegBeginAddr
      else:
        more_points = False

####
# search_nodes displays nodes close to a given lat & lon location
####
def search_nodes(map):
  if len(map.nodeList) > 0:
    valid, lat, lon = parse_gps()
    if not valid:
      return
    dlist = map.generate_dlist(lat, lon)
    dlist_sorted = sorted(dlist)
    show_type = input("Show (1) nodes closer than a certain distance, or (2) given number of closest nodes: ")
    show_num = 0
    if show_type == '1':
      keepTrying = 'y'
      while keepTrying == 'y':
        dist_str = input("Show nodes closer than the following distance (in feet): ")
        try:
          dist_num = int(dist_str)
          show_num = sum([CvtdUtil.coord_to_ft(y) < dist_num for y in dlist])
          show = input(f"Show {show_num} entries (y/n): ")
          if show == 'y':
            print(f"Showing {show_num} nodes within {dist_num} feet of {lat}, {lon}")
            for i in range(show_num):
              dlist_ix = dlist.index(dlist_sorted[i])
              e = round(CvtdUtil.coord_to_ft(dlist_sorted[i]), 3)
              print(f"{i+1}: {map.nodeList[dlist_ix].lat}, {map.nodeList[dlist_ix].lon} ({e} feet)")
            keepTrying = 'n'
          else:
            keepTrying = input("Try again (y/n): ")
        except ValueError:
          keepTrying = input(f"Error: Could not convert ${show_str} to an integer. Try again (y/n): ")
    elif show_type == '2':
      nnodes = len(map.nodeList)
      show_str = input(f"Show how many entries (max {nnodes}): ")
      try:
        show_num = min(int(show_str), nnodes)
        print(f"Showing {show_num} nodes close to {lat}, {lon}")
        for i in range(show_num):
          dlist_ix = dlist.index(dlist_sorted[i])
          e = round(dlist_sorted[i]*70*5280, 3)
          print(f"{i+1}: {map.nodeList[dlist_ix].lat}, {map.nodeList[dlist_ix].lon} ({e} feet)")
      except ValueError:
        print(f"Error: Could not convert ${show_str} to an integer")
  
    # Now, let them choose one of these nodes
    if show_num > 0:
      while True:
        try:
          node_info = int(input(f"Get more info about a node (1-{show_num}) or (n)o: "))
          if 1 <= node_info <= show_num:
            plist = map.get_node_usage(dlist.index(dlist_sorted[node_info - 1]))
            if len(plist) > 0:
              print("The following roads use this node: ")
              for p in plist:
                print(p.addr_repr(map.roadList))
          else:
            break
        except ValueError:
          break
  else:
    print("No nodes have been added, you might want to read roads.txt (key 'r')")

####
# show_help() prints a help message to the screen
####
def show_help():
  print("(1) Add new street")
  print("(2) Search streets")
  print("(3) Add new node")
  print("(4) Search nodes")
  print("(5) Add new route")
  print("(6) Search routes")
  print("(7) Add new city")
  print("(8) Search cities")
  print("(9) Add new landmark")
  print("(10) Search landmarks")
  print("(r) Read roads file")
  print("(w) Write roads file")
  print("(v) Validate current map")
  print("(q) Quit")
  
####
# get_filename parses a read or write command, and returns filename if given, else roads.txt
#
# command (should start with (r)ead or (w)rite), then filename if desired
#
# return[0] is the requested or default filename
####
def get_filename(command):
  words = [a.strip() for a in command.strip().split()]
  if len(words) <= 1:
    return "roads.txt"
  else:
    return words[1]

def main():
  map = CvtdMap()
  command = "help"
  while command not in ["quit", "exit", "q", "e"]:
    if command == "1":
      new_street(map)
    elif command == "2":
      search_streets(map)
    elif command == "3":
      pass
    elif command == "4":
      search_nodes(map)
    elif command == "5":
      new_route(map)
    elif command == "6":
      pass
    elif command == "7":
      pass
    elif command == "8":
      pass
    elif command == 'v':
      map.validate()
    elif command.lower().strip().split()[0] in ['r', 'read', 'o', 'open']:
      map.read_roads(get_filename(command))
    elif command.lower().strip().split()[0] in ['w', 'write', 's', 'save']:
      map.write_roads(get_filename(command))
    else:
      show_help()
    command = input("\n>>> ")

  print("ROAD LIST COUNT = {}".format(len(map.roadList)))
    
  
if __name__ == '__main__':
  main()

  
