#!bin/usr/env python

# TODO:
# IMPLEMENT ability to add routes in roadtool
# ADD ability to cvtdapp to read nodes, streets and routes from file
# IMPLEMENT ability to dump nodes, streets and routes from roadtool
# CHANGE logic to detect percent completion of street, route

import math
import os
import threading
import time
import xml.etree.ElementTree as ET

######################################################################################

# Before ROUTEFIX:

# ROUTE_LIST[key] gives a ROUTE with variable number of components
# ROUTE_LIST[key][0] gives a segment with 3+ components
# ROUTE_LIST[key][3] gives the first stop on that segment

ROUTE_LIST = {
	"ORANGE": 
		[[41.743732, -111.814055, 
			[41.743732, -111.814055, "TSC"]],
		[41.743776, -111.814163, 
			[41.758993, -111.813783, "ASTE"]],
		[41.761022, -111.813819],
		[41.761098, -111.815682],
		[41.761206, -111.816129],
		[41.761294, -111.818939],
		[41.762146, -111.818952,
			[41.762213, -111.819879, "Innovation"]],
		[41.762156, -111.820692],
		[41.761338, -111.820712],
		[41.761196, -111.820489,
			[41.761036, -111.817269, "USTAR"]],
		[41.76102, -111.813817, 
			[41.751484, -111.814008, "Blue Square"]],
		[41.743781, -111.814168],
		[41.743717, -111.814284],
		[41.743456, -111.814201],],

	"#2":
		[["500 N", 150, 200,
			[41.74089, -111.830632, "150 E 500 N"]],
		["200 E", 500, 1000,
			[41.742988, -111.829461, "604 N 200 E"],
			[41.744929, -111.829449, "704 N 200 E"],
			[41.748844, -111.829353, "918 N 200 E"],
			[41.753042, -111.829203, "1206 N 200 E"],
			[41.756348, -111.829114, "1360 N 200 E"]],
		["1400 N", 200, 600,
			[41.75748, -111.826417, "330 E 1400 N"],
			[41.75746, -111.822197, "465 E 1400 N"]],
		["600 E", 1400, 1650,
			[41.760497, -111.818968, "1500 N 600 E"]],
		["1650 N", 600, 500],
		["Research Park Way, North Logan", 1650, 1800,
			[41.763569, -111.821092, "1750 N Research Park Way"]],
		["1800 N", 550, 800,
			[41.764881, -111.819167, "1800 N 600 E"]],
		["800 E", 1800, 1000,
			[41.763819, -111.813734, "1775 N 800 E"],
			[41.759013, -111.813862, "1521 N 800 E"],
			[41.756687, -111.813822, "1380 N 800 E"],
			[41.753351, -111.813889, "1200 N 800 E"],
			[41.751704, -111.813895, "1111 N 800 E"]],
		["1000 N", 800, 600,
			[41.749925, -111.816991, "695 East 1000 North"]],
		["600 E", 1000, 1400,
			[41.751199, -111.819264, "1090 N 600 E"],
			[41.755687, -111.819079, "1320 N 600 E"]],
		["1400 N", 600, 200,
			[41.75742, -111.820473, "545 E 1400 N"],
			[41.757475, -111.826113, "330 E 1400 N"]],
		["200 E", 1400, 700,
			[41.7562, -111.829126, "1365 N 200 E"],
			[41.75282, -111.829217, "1201 N 200 E"],
			[41.749657, -111.829325, "979 N 200 E"]],
		["700 N", 200, 100,
			[41.744699, -111.830507, "165 E 700 N"]],
		["100 E", 700, 500],
		["500 N", 100, 150],
	]
}

######################################################################################

# After ROUTEFIX:

# ROUTE_LIST[key] gives a ROUTE with two components
# ROUTE_LIST[key][0] gives the points on the ROUTE, a variable length list
# ROUTE_LIST[key][0][0] gives the first POINT, where each point has three components
# ROUTE_LIST[key][0][0][0] gives the latitude of the first POINT
# ROUTE_LIST[key][1] gives the stops on the ROUTE, a variable length list
# ROUTE_LIST[key][1][0] gives the first STOP, where each stop has three components
# ROUTE_LIST[key][1][0][0] gives the latitude of the first STOP

######################################################################################

ROUTE_MAP = {
	"Route  1" : "#1",
	"Route  2" : "#2",
	"Route 3" : "#3",
	"Route  5" : "#5",
	"Route  6" : "#6",
	"Route  7" : "#7",
	"Route  8" : "#8",
	"Route  9" : "#9",
	"Route 10" : "#10",
	"Route 11" : "#11",
	"Route 12" : "#12",
	"Route 13" : "#13",
	"Route 14" : "#14",
	"Route 15" : "#15",
	"Route 16 AM" : "#16",
	"Route 16 PM" : "#16",
	"Blue Loop 1" : "BLUE",
	"Blue Loop 2" : "BLUE",
	"Blue Loop Peak 1" : "BLUE",
	"Blue Loop Peak 2" : "BLUE",
	"Green Loop 1" : "GREEN",
	"Green Loop 2" : "GREEN",
	"Green Loop Peak 1" : "GREEN",
	"Green Loop Peak 2" : "GREEN",
}

######################################################################################

DATA_DROP = [
	["ORANGE", "2/25/2020", "10:59:00 AM", 41.755532, -111.813898],
	["ORANGE", "2/25/2020", "10:59:30 AM", 41.757241, -111.813807],
	["ORANGE", "2/25/2020", "11:00:00 AM", 41.757241, -111.813807],
	["ORANGE", "2/25/2020", "11:00:30 AM", 41.757241, -111.813807],
	["ORANGE", "2/25/2020", "11:01:00 AM", 41.758978, -111.81384],
	["ORANGE", "2/25/2020", "11:01:30 AM", 41.761035, -111.81429],
	["ORANGE", "2/25/2020", "11:02:00 AM", 41.761267, -111.8165],
	["ORANGE", "2/25/2020", "11:02:30 AM", 41.761267, -111.8165],
	["ORANGE", "2/25/2020", "11:03:00 AM", 41.762179, -111.820556],
	["ORANGE", "2/25/2020", "11:03:30 AM", 41.761139, -111.819429],
	["ORANGE", "2/25/2020", "11:04:00 AM", 41.761086, -111.816891],
	["ORANGE", "2/25/2020", "11:04:30 AM", 41.761062, -111.814729],
	["ORANGE", "2/25/2020", "11:05:00 AM", 41.760529, -111.813819],
	["ORANGE", "2/25/2020", "11:05:30 AM", 41.757978, -111.813835],
	["ORANGE", "2/25/2020", "11:06:00 AM", 41.757469, -111.813835],
	["ORANGE", "2/25/2020", "11:06:30 AM", 41.757312, -111.813848],
	["ORANGE", "2/25/2020", "11:07:00 AM", 41.75253, -111.813919],
	["ORANGE", "2/25/2020", "11:07:30 AM", 41.751531, -111.81388],
	["ORANGE", "2/25/2020", "11:08:00 AM", 41.750636, -111.813868],
	["ORANGE", "2/25/2020", "11:08:30 AM", 41.745765, -111.814096],
	["ORANGE", "2/25/2020", "11:09:00 AM", 41.743609, -111.814274],
	["ORANGE", "2/25/2020", "11:09:30 AM", 41.743747, -111.814077],
	["ORANGE", "2/25/2020", "11:10:00 AM", 41.743747, -111.814077],
	["ORANGE", "2/25/2020", "11:10:30 AM", 41.744499, -111.814108],
	["ORANGE", "2/25/2020", "11:11:00 AM", 41.745836, -111.814051],
	["ORANGE", "2/25/2020", "11:11:30 AM", 41.750267, -111.813879],
	["ORANGE", "2/25/2020", "11:12:00 AM", 41.754445, -111.81387],
	["ORANGE", "2/25/2020", "11:12:30 AM", 41.758295, -111.813859],
	["ORANGE", "2/25/2020", "11:13:00 AM", 41.759239, -111.81387],
	["ORANGE", "2/25/2020", "11:13:30 AM", 41.761088, -111.815131],
	["ORANGE", "2/25/2020", "11:14:00 AM", 41.7613, -111.81887],
	["ORANGE", "2/25/2020", "11:14:30 AM", 41.762096, -111.818955],
	["ORANGE", "2/25/2020", "11:15:00 AM", 41.761976, -111.820715],
]

######################################################################################

# BUS_LOC is indexed by bus ID
# BUS_LOC[busId] is a list, where [0] is time and [1, 2, 3] are GPS latitude, longitude and heading

BUS_LOC = {};

######################################################################################

####
# routefix converts a route from the human-readable format to the easier to use format
#
# route is the list indicating the route (likely indexed from ROUTE_LIST)
#
# return[0] is the new list indicating the fixed route
####
def routefix(route):
	points = route
	result = ''

	# First, generate the points
	result = '['
	stops_result = ''
	s = '['
	for p_ix, p in enumerate(points):
		ix, seg_ix, proj_ratio, error = compute_proj_ratio(p[0], p[1], None)

		p_next_ix = (p_ix + 1) % len(points);

		heading = round(math.degrees(math.atan2(points[p_next_ix][1] - p[1], points[p_next_ix][0] - p[0])))
		s = s + '[' + str(ix) + ", " + str(seg_ix) + ", " + str(round(proj_ratio, 6)) + ', ' + str(heading) + '],'
		s = s + '\t# ' + compute_addr(p[0], p[1], None)[0]
		result = result + s + '\n'
		s = ''

		# Add any stops associated with this segment
		for stop in p[2:]:
			blat = p[0]
			blon = p[1]
			elat = points[p_next_ix][0]
			elon = points[p_next_ix][1]
			street_sc, pos_sc, projection_sc, begin_or_end = sub_proj_ratio(stop[0], stop[1], blat, blon, elat, elon)
			if begin_or_end == 0:
				projection_sc = street_sc - projection_sc
			stop_proj_ratio = projection_sc / street_sc

			stop_s = '[' + str(p_ix) + ", " + str(round(stop_proj_ratio, 6)) + ", '" + stop[2] + "'],"
			stops_result = stops_result + stop_s + '\n'
	
	# Next, generate the stops
	result = result + '], \n[' + stops_result + ']]'
	return result

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

def pull(count, key):
	if not 1 <= count <= 5:
		print("Error [pull]: Count must be between 1 and 5")
		return

	pull_data(key)

	print_list = {}
	for i in range(count):
		for bnum in BUS_LOC:
			add_to_print_list(print_list, bnum, -1 - i)

	print_print_list(print_list, count)

######################################################################################

g_fastPullRunning = False
fastPullDelay = 0.5

def fastpull_main(max_counter, key):
	counter = max_counter
	while g_fastPullRunning == True:
		if counter == max_counter:
			new_elements = pull_data(key)
			if len(new_elements) > 0:
				print('')
				print_list = {}
				for bnum, ix in new_elements:
					add_to_print_list(print_list, bnum, ix)
				print_print_list(print_list, 5)
				print("\n>>> ", end="")

				counter = 0
		counter = counter + fastPullDelay
		time.sleep(fastPullDelay)
	

######################################################################################

def main():
	global g_fastPullRunning

	with open('key.txt', 'r') as f:
		key = f.read()
	fastpull_thread = None

	while True:
		text_in = input(">>> ")
		text_spl = text_in.strip().split()
		if len(text_in) == 0:
			continue
		if text_in.lower() in ['exit', 'e', 'exit()', 'quit', 'q']:
			if g_fastPullRunning == True:
				g_fastPullRunning = False
				fastpull_thread.join()
			break
		elif text_in.lower() in ['help', 'usage', 'h', 'u']:
			print("{: <24}Bring up this help page".format("help"))
			print("{: <24}Quits the app".format("quit"))
			print("{: <24}Computes an address for the provided latitude and longitude".format("addr [lat] [lon]"))
			print("{: <24}Converts a route from latitude and longitude to street and proj ratio".format("routefix [route]"))
			print("{: <24}Prints address and route completion for data drop for given route".format("datadrop [route]"))
			print("{: <24}Prints percent complete for given point of given route".format("ppt [route] [pointix]"))
			print("{: <24}Pulls current bus locations and prints most recent # locations".format("pull [# points]"))
		elif text_spl[0].lower() == 'addr':
			try:
				addr, error = compute_addr(float(text_spl[1]), float(text_spl[2]), None)
				print(addr)
				print("Error: {} feet".format(round(error, 3)))
			except IndexError:
				print("Error [addr]: Please specify latitude and longitude")
			except ValueError:
				print("Error [addr]: Please specify latitude and longitude in floating-point format")
		elif text_spl[0].lower() == 'routefix':
			try:
				print(routefix(ROUTE_LIST[text_spl[1]]))
			except IndexError:
				print("Error [routefix]: Please provide the name of the route to fix")
			except KeyError:
				print("Error [routefix]: Route {} does not exist".format(text_spl[1]))
		elif text_spl[0].lower() == 'datadrop':
			try:
				print(datadrop(ROUTE_LIST[text_spl[1]]))
			except IndexError:
				print("Error [datadrop]: Please provide the name of the route to consider")
			except KeyError:
				print("Error [datadrop]: Route {} does not exist".format(text_spl[1]))
		elif text_spl[0].lower() == 'ppt':
			try:
				route = eval(routefix(ROUTE_LIST[text_spl[1]]))
				print("{}%".format(100 * compute_route_completion(route[0], int(text_spl[2]), 0)))
			except IndexError:
				print("Error [ppt]: Please provide the name of the route and the index of the point")
			except KeyError:
				print("Error [ppt]: Route {} does not exist".format(text_spl[1]))
			except ValueError:
				print("Error [ppt]: Point {} could not be converted to an integer".format(text_spl[2]))
		elif text_spl[0].lower() == 'spt':
			try:
				route = eval(routefix(ROUTE_LIST[text_spl[1]]))
				segment_ix = int(text_spl[2])
				print("{}%".format(100 * compute_route_completion(route[0], route[1][segment_ix][0], route[1][segment_ix][1])))
			except IndexError:
				print("Error [spt]: Please provide the name of the route and the index of the point")
			except KeyError:
				print("Error [spt]: Route {} does not exist".format(text_spl[1]))
			except ValueError:
				print("Error [spt]: Point {} could not be converted to an integer".format(text_spl[2]))
		elif text_spl[0].lower() == 'pull':
			try:
				pull(int(text_spl[1]), key)
			except ValueError:
				print("Error [pull]: Number of points {} could not be converted to an integer".format(text_spl[1]))
			except IndexError:
				pull(1, key)
		elif text_spl[0].lower() == 'fastpull':
			if g_fastPullRunning:
				g_fastPullRunning = False
				fastpull_thread.join()
				fastpull_thread = None
			else:
				g_fastPullRunning = True
				try:
					fastpull_thread = threading.Thread(target=fastpull_main, args=(float(text_spl[1]), key))
					fastpull_thread.start()
				except ValueError:
					print("Error [fastpull]: Pull delay {} could not be converted to an float".format(text_spl[1]))
					g_fastPullRunning = False
				except IndexError:
					fastpull_thread = threading.Thread(target=fastpull_main, args=(5.0, key))
					fastpull_thread.start()

		print("")

if __name__ == '__main__':
	main()
