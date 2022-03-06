#!/usr/bin/python3
import datetime
import math
import os

from cvtdBus import CvtdBus
from cvtdContainedRoadPoint import ContainedRoadPoint
from cvtdMap import CvtdMap
from cvtdNode import CvtdNode
from cvtdRoad import CvtdRoad
from cvtdRoadPoint import CvtdRoadPoint
from cvtdRoute import CvtdRoute
from cvtdRouteSegment import CvtdRouteSegment
from cvtdUtil import CvtdUtil
from importer import Importer

# TO DO:
#  Test roadTool!
#  Update cvtdapp.py
#  Change roads.txt so that it takes less space and is not a text file, and record routes
#  Write OSM reader
#  Execute OSM reader to get a better roads.txt file
#  Store bus locations to disk

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
  if action=='1':
    new_road = define_road_details()
    new_road.points = map.roadList[ix].points
    map.roadList[ix] = new_road
  elif action=='2':
    new_road = define_road_points(map, map.roadList[ix])
    if new_road is not None:
      map.roadList[ix] = new_road
  elif action=='3':
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
# import_osm opens up the provided OSM file and read nodes and roads, helping user to add them into myMap
####
def import_osm(myMap):
  filePath = input("Enter the absolute or relative path to the OSM file: ")
  if filePath != "":
    Importer.begin_import(filePath, myMap)
    show_help()

####
# new_node allows the user to add a node
####
def new_node(map):
  valid, lat, lon = parse_gps()
  dlist = map.generate_dlist(lat, lon)
  dlist_sorted = sorted(dlist)
  dlist_ix = dlist.index(dlist_sorted[0])
  node = self.nodeList[dlist_ix]
  c = input(f"The closest node is at ({node.lat}, {node.lon}), about {CvtdUtil.coord_to_ft(dlist_sorted[0])} ft away. Continue?") == 'y'
  if c:
    self.nodeList.append(CvtdNode(lat, lon))
    print(f"Node added successfully. There are now {len(self.nodeList)} nodes.")

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
  print("(11) Import Google Transit files")
  print("(12) Import OpenStreetMap files")
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
  myMap = CvtdMap()
  command = "help"
  while command not in ["quit", "exit", "q", "e"]:
    if command == "1":
      new_street(myMap)
    elif command == "2":
      search_streets(myMap)
    elif command == "3":
      pass
    elif command == "4":
      search_nodes(myMap)
    elif command == "5":
      new_route(myMap)
    elif command == "6":
      pass
    elif command == "7":
      pass
    elif command == "8":
      pass
    elif command == "11":
      myMap.import_google_directory()
    elif command == "12":
      import_osm(myMap)
    elif command == 'v':
      myMap.validate()
    elif command.lower().strip().split()[0] in ['r', 'read', 'o', 'open']:
      myMap.read_roads(get_filename(command))
    elif command.lower().strip().split()[0] in ['w', 'write', 's', 'save']:
      myMap.write_roads(get_filename(command))
    else:
      show_help()
    command = input("\n>>> ")

  print("ROAD LIST COUNT = {}".format(len(myMap.roadList)))
    
  
if __name__ == '__main__':
  main()

