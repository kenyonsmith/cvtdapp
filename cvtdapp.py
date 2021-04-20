import xml.etree.ElementTree as ET

from cvtdContainedRoadPoint import ContainedRoadPoint
from cvtdMap import CvtdMap
from cvtdNode import CvtdNode
from cvtdRoad import CvtdRoad
from cvtdRoadPoint import CvtdRoadPoint
from cvtdRoute import CvtdRoute
from cvtdRouteSegment import CvtdRouteSegment
from cvtdUtil import CvtdUtil

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
				fmt = fmt.format(print_list[info][i+1][0], print_list[info][i+1][1], str(print_list[info][i+1][2]) + " feet", print_list[info][i+1][3])
			except IndexError:
				pass
		print(fmt)

####
# add_to_print_list 
#
# print_list
# bnum
# ix
####
def add_to_print_list(print_list, bnum, ix):
	try:
		t, route, lat, lon, direction = BUS_LOC[bnum][ix]
	except IndexError:
		return

	# Determine route
	valid_streets = None
	try:
		rname = ROUTE_MAP[route]
		if rname in ROUTE_LIST:
			route_fixed = eval(routefix(rname))
			valid_streets = set(a[0] for a in route_fixed[0])
	except KeyError:
		print('Warning: Route "{}" could not be found in route map'.format(route))
	except IndexError:
		return

	# Compute address
	addr, error = compute_addr(lat, lon, valid_streets)
	if valid_streets is not None and error > 250:
		addr_off_route, error_off_route = compute_addr(lat, lon, None)
		if error_off_route < 200:
			addr = "!" + addr_off_route 
			error = error_off_route
	error = round(error)

	# Determine if direction is actual or if it should be X
	try:
		lat_to_lat_diff = abs((BUS_LOC[bnum][ix - 1][2] - lat))*70*5280
		lon_to_lon_diff = abs((BUS_LOC[bnum][ix - 1][3] - lon))*70*5280
		pos_to_pos_diff = math.sqrt(lat_to_lat_diff ** 2 + lon_to_lon_diff ** 2)
		if (pos_to_pos_diff < 40):
			direction = 'X'
		else:
			direction = get_direction(direction)
	except IndexError:
		direction = get_direction(direction)

	# Add to list to print later
	try:
		print_list[bnum].append([t, addr, error, direction])
	except KeyError:
		print_list[bnum] = [route]
		print_list[bnum].append([t, addr, error, direction])

####
# pull_data pulls the XML feed and does [what] with it
#
# key
####
def pull_data(key):
	NUM_ELEMENTS = 5
	new_elements = []

	os.system("curl -o cvtddata.txt http://cvtd.info:8080/CVTDfeed/V200/XML/_System.php?key={} -s".format(key))
	tree = ET.parse('cvtddata.txt')
	root = tree.getroot()
	for bus in root:
		for i in range(NUM_ELEMENTS - 1, 0, -1):
			try:
				bnum = bus[3].text
				route = bus[5].text
				t = bus[8][i].text.strip().split()[1].split('.')[0]
				lat = float(bus[8][i][0].text)
				lon = float(bus[8][i][1].text)
				direction = int(bus[8][i][2].text)
				if lat == 0.0 and lon == 0.0:
					continue
			except IndexError:
				continue

			entry_exists = False
			try:
				entry_exists = t in [e[0] for e in BUS_LOC[bnum]]
			except KeyError:
				entry_exists = False
				BUS_LOC[bnum] = []

			if not entry_exists:
				BUS_LOC[bnum].append((t, route, lat, lon, direction))
				new_elements.append((bnum, len(BUS_LOC[bnum]) - 1))
	return new_elements

####
# pull
#
# map
# count
# key
####
def pull(map, count, key):
	if not 1 <= count <= 5:
		print("Error [pull]: Count must be between 1 and 5")
		return

	pull_data(key)

	print_list = {}
	for i in range(count):
		for bnum in BUS_LOC:
			add_to_print_list(print_list, bnum, -1 - i)

	print_print_list(print_list, count)

####
# show_help prints a help message to the screen
####
def show_help():
	print("(1) Pull XML feed")
	print("(r) Read roads file")
	print("(q) Quit")

####
# main is the application entry point
####
def main():
	with open('key.txt', 'r') as f:
		key = f.read()

	map = CvtdMap()
	command = "help"
	while command not in ["quit", "exit", "q", "e"]:
		if command == "1":
			pull(map, 1, key)
		elif command.lower().strip().split()[0] in ['r', 'read', 'o', 'open']:
			map.read_roads(get_filename(command))
		else:
			show_help()
		command = input("\n>>> ")
	
if __name__ == '__main__':
	main()