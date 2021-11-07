#!/usr/bin/python3
from datetime import datetime
import math
import os
import xml.etree.ElementTree as ET

from cvtdBusLocator import CvtdBusLocator
from cvtdBusPosition import CvtdBusPosition
from cvtdContainedRoadPoint import ContainedRoadPoint
from cvtdMap import CvtdMap
from cvtdNode import CvtdNode
from cvtdRoad import CvtdRoad
from cvtdRoadPoint import CvtdRoadPoint
from cvtdRoute import CvtdRoute
from cvtdRouteSegment import CvtdRouteSegment
from cvtdUtil import CvtdUtil
import direction
from direction import Direction

####
# print_print_list
#
# print_list
# count
####
def print_print_list(print_list, count):
	for info in print_list:
		fmt = "{: <" + str(2+max([len(print_list[key][0]) for key in print_list.keys()])) + "}"
		fmt = fmt.format(print_list[info][0])
		for i in range(count):
			try:
				fmt = fmt + "{}: {: <" + str(2+max([len(print_list[key][i+1][1]) for key in print_list])) + "}{: <10}{: <3}| "
				#print(max([print_list[key][i][0] for key in print_list]))
				fmt = fmt.format(print_list[info][i+1][0].strftime("%H:%M:%S"),
					print_list[info][i+1][1],
					str(print_list[info][i+1][2]) + " feet",
					print_list[info][i+1][3].short_str())
			except IndexError:
				pass
		print(fmt)

####
# add_to_print_list adds an entry to the print list for formatting and printing later
#  We use a print list so that we can compute the address of each bus, and use
#  the shortest amount of whitespace that will work with all of the buses
#  print_list is a dictionary, where bus number is a key
#  print_list[key][0] is the route name
#  print_list[key][1+j][0] is timestamp
#  print_list[key][1+j][1] is address
#  print_list[key][1+j][2] is error
#  print_list[key][1+j][3] is direction as a Direction class
#
# myMap is the CvtdMap, used to get list of valid streets for route 
# locator is the CvtdBusLocator
# print_list is the print list we are adding to
# rid is the bus route id (key into locator) that we are adding to print list
# ix is the index into the locator's list of positions, most likely negative
####
def add_to_print_list(myMap, locator, print_list, rid, ix):
	try:
		position = locator.pos[rid][ix]
		t = position.timestamp
		lat = position.lat
		lon = position.lon
		dir = position.direction
	except IndexError:
		return

	# Determine route
	route = myMap.find_route_by_rid(rid)
	try:
		routeName = route.name
		validStreets = route.get_street_list()
	except AttributeError:
		routeName = "Unknown Route"
		validStreets = None

	# Compute address
	roadIx, addr, error = myMap.compute_addr_repr(lat, lon, validStreets)
	if validStreets is not None and error > 250:
		roadIx, addr_off_route, error_off_route = myMap.compute_addr_repr(lat, lon, None)
		if error_off_route < 200:
			addr = "!" + addr_off_route 
			error = error_off_route
	error = round(error)

	# Determine if direction is actual or if it should be X
	try:
		lat_to_lat_diff = CvtdUtil.coord_to_ft(abs(locator.pos[rid][ix - 1].lat - lat))
		lon_to_lon_diff = CvtdUtil.coord_to_ft(abs(locator.pos[rid][ix - 1].lon - lon))
		pos_to_pos_diff = math.sqrt(lat_to_lat_diff ** 2 + lon_to_lon_diff ** 2)
		if (pos_to_pos_diff < 40):
			dir = Direction.X
		else:
			dir = direction.get_direction(dir)
	except IndexError:
		dir = direction.get_direction(dir)

	# Add to list to print later
	try:
		print_list[rid].append([t, addr, error, dir])
	except KeyError:
		print_list[rid] = [routeName]
		print_list[rid].append([t, addr, error, dir])

####
# pull_data pulls the XML feed and adds new positions to the Bus Locator, also returns new positions
#
# key is the text to insert into the URL
# locator is the Bus Locator where new positions will be added
#
# return is a set of bus route ids (keys into locator) with new data
####
def pull_data(key, locator):
	NUM_ELEMENTS = 5
	newElements = set()

	os.system("curl -o cvtddata.txt http://cvtd.info:8080/CVTDfeed/V200/XML/_System.php?key={} -s".format(key))
	tree = ET.parse('cvtddata.txt')
	root = tree.getroot()
	for bus in root:
		for i in range(NUM_ELEMENTS - 1, 0, -1):
			try:
				rid = int(bus[2].text)
				bnum = bus[3].text
				rnum = bus[4].text
				route = bus[5].text
				t = datetime.strptime(bus[8][i].text.strip(), "%Y-%m-%d %H:%M:%S.%f")
				lat = float(bus[8][i][0].text)
				lon = float(bus[8][i][1].text)
				direction = int(bus[8][i][2].text)
				if lat == 0.0 and lon == 0.0:
					continue

				entry = locator.find(rid, t)
				if entry is None:
					newPos = CvtdBusPosition(t, lat, lon, direction)
					newElements.add(rid)
					locator.insert_append(rid, newPos)
			except (IndexError, ValueError):
				continue
	return newElements

####
# pull pulls data from the XML feed, updates the locator, and prints new positions to the screen
#
# myMap is the CvtdMap
# locator is the CvtdBusLocator
# count is the number of positions to print for each bus, 1-5
# key is the text to insert into the URL
####
def pull(myMap, locator, count, key):
	if not 1 <= count <= 5:
		print("Error [pull]: Count must be between 1 and 5")
		return

	newElements = pull_data(key, locator)

	# Generate print list so that formatting can be aligned
	print_list = {}
	for i in range(count):
		for element in newElements:
			add_to_print_list(myMap, locator, print_list, element, -1 - i)

	# Print everything in the print list
	print_print_list(print_list, count)

####
# list_locator prints all positions stored in locator to the screen
#
# myMap is the CvtdMap
# locator is the CvtdBusLocator
# command is the command used, to be parsed for a route number. Else route number will be queried
####
def list_locator(myMap, locator, command):
	words = command.split()
	if len(words) == 1:
		word = input("Enter route number to display: ")
		words.append(word)
	if len(words) >= 2:
		print_list = {}
		for word in words[1:]:
			import pdb; pdb.set_trace()
			try:
				for ix in range(len(locator.pos[word])):
					route = myMap.find_route_by_rnum(word)
					add_to_print_list(myMap, locator, print_list, route.buses[0].id, ix)
			except KeyError:
				print(f"Error: Unknown route: {word}")
		print_print_list(print_list, 1)
  
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

####
# show_help prints a help message to the screen
####
def show_help():
	print("(1) Pull XML feed")
	print("(2) List locator positions")
	print("(r) Read roads file")
	print("(q) Quit")

####
# main is the application entry point
####
def main():
	with open('key.txt', 'r') as f:
		key = f.read()

	myMap = CvtdMap()
	locator = CvtdBusLocator('locator/')
	locator.read_locator()
	command = "help"
	while command not in ["quit", "exit", "q", "e"]:
		if command == "1":
			pull(myMap, locator, 1, key)
		elif command[0] == "2":
			list_locator(myMap, locator, command)
		elif command.lower().strip().split()[0] in ['r', 'read', 'o', 'open']:
			myMap.read_roads(get_filename(command))
		else:
			show_help()
		command = input("\n>>> ")
	
if __name__ == '__main__':
	main()

