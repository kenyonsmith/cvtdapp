#!bin/usr/env python

import math
import os
import xml.etree.ElementTree as ET

ROAD_LIST = [
# MAIN STREET
	["Main Street, Smithfield", 41.853007, -111.831818, 41.846866, -111.832402, 800, 492, "N/S"],
	["Main Street, Smithfield", 41.846866, -111.832402, 41.823952, -111.832988, 492, -600, "N/S"],
	["Main Street, Smithfield", 41.823952, -111.832988, 41.812785, -111.833177, -600, -1200, "N/S"],
	["Main Street, Hyde Park", 41.812785, -111.833177, 41.787613, -111.83375, 4400, 3100, "N/S"],
	["Main Street, North Logan", 41.787613, -111.83375, 41.761347, -111.834305, 3100, 1600, "N/S"],
	["Main Street", 41.761347, -111.834305, 41.717425, -111.835328, 1600, -800, "N/S"],
	["Main Street", 41.717425, -111.835328, 41.716106, -111.834923, -800, -880, "N/S"],
	["Main Street", 41.716106, -111.834923, 41.710208, -111.834623, -880, -1200, "N/S"],
	["Main Street", 41.710208, -111.834623, 41.691065, -111.83423, -1200, -2300, "N/S"],
	["Main Street", 41.691065, -111.83423, 41.685493, -111.83384, -2300, -2600, "N/S"],
	["Main Street, Nibley", 41.685493, -111.83384, 41.651093, -111.832748, -2600, -4400, "N/S"],
	["800 E, Hyrum", 41.651093, -111.832748, 41.621668, -111.832674, 800, -550, "N/S"],
	["US-89", 41.717425, -111.835328, 41.714348, -111.836977, -800, -992, "N/S"],
	["US-89", 41.714348, -111.836977, 41.692821, -111.865738, -992, -2200, "N/S"],
	["US-89", 41.692821, -111.865738, 41.66172, -111.896854, -2200, -3900, "N/S"],

# SMITHFIELD
	["100 N, Smithfield", 41.838728, -111.843833, 41.838533, -111.826995, -400, 200, "E/W"],
	["100 S, Smithfield", 41.834564, -111.8439, 41.834234, -111.824263, -400, 300, "E/W"],
	["400 S, Smithfield", 41.828356, -111.844013, 41.828006, -111.824512, -400, 300, "E/W"],
	["600 S, Smithfield", 41.823959, -111.832991, 41.823963, -111.826354, 0, 250, "E/W"],
	["100 E, Smithfield", 41.844866, -111.829584, 41.828111, -111.830048, 400, -400, "N/S"],
	["250 E, Smithfield", 41.828026, -111.826179, 41.823948, -111.826351, -400, -600, "N/S"],
	["300 E, Smithfield", 41.834234, -111.824263, 41.828006, -111.824512, -100, -400, "N/S"],

# HYDE PARK
	["250 E, Hyde Park", 41.796406, -111.812771, 41.784067, -111.813083, -124, -760, "N/S"],

# LOGAN, NORTH LOGAN EAST/WEST STREETS
	["2860 N, North Logan", 41.78342, -111.833836, 41.783429, -111.830904, 0, 100, "E/W"],
	["2600 N, North Logan", 41.780029, -111.833895, 41.779924, -111.822801, 0, 400, "E/W"],
	["2200 N, North Logan", 41.772519, -111.838813, 41.771893, -111.804488, -200, 1200, "E/W"],
	["1800 N"             , 41.765463, -111.858613, 41.764957, -111.834231, -1000, 0, "E/W"],
	["1800 N, North Logan", 41.764957, -111.834231, 41.764727, -111.808656, 0, 1000, "E/W"],
	["1650 N, North Logan", 41.762189, -111.823792, 41.762175, -111.822317, 400, 450, "E/W"],
	["1650 N, North Logan", 41.762175, -111.822317, 41.762475, -111.821306, 450, 500, "E/W"],
	["1650 N, North Logan", 41.762475, -111.821306, 41.762162, -111.820702, 500, 525, "E/W"],
	["1650 N, North Logan", 41.762162, -111.820702, 41.762152, -111.818947, 525, 600, "E/W"],
	["1605 N, North Logan", 41.761335, -111.820258, 41.761023, -111.813817, 572, 708, "E/W"],
	["1605 N, North Logan", 41.761023, -111.813817, 41.761083, -111.815643, 708, 727, "E/W"],
	["1600 N"             , 41.761479, -111.843905, 41.761332, -111.834297, -400, 0, "E/W"],
	["1600 N, North Logan", 41.761332, -111.834297, 41.760968, -111.823873, 0, 400, "E/W"],
	["1600 N, North Logan", 41.761215, -111.820703, 41.761023, -111.813817, 532, 800, "E/W"],
	["1500 N", 41.758451, -111.800803, 41.758441, -111.789863, 1325, 1800, "E/W"],
	["1400 N", 41.758164, -111.878686, 41.75716, -111.803584, -1800, 1229, "E/W"],
	["1400 N", 41.75716, -111.803584, 41.758451, -111.800803, 1229, 1325, "E/W"],
	["1000 N", 41.750848, -111.888523, 41.749879, -111.817269, -2210, 669, "E/W"],
	["1000 N", 41.749879, -111.817269, 41.750183, -111.815602, 669, 728, "E/W"],
	["1000 N", 41.750183, -111.815602, 41.74999, -111.80436, 728, 1200, "E/W"],
	["1000 N", 41.749298, -111.804378, 41.74937, -111.799496, 1200, 1400, "E/W"],
	["Ellendale Ave", 41.74937, -111.799496, 41.749446, -111.794506, 1400, 1600, "E/W"],
	["700 N", 41.744747, -111.834601, 41.744492, -111.816656, 0, 700, "E/W"],
	["Aggie Blvd", 41.744558, -111.815825, 41.744145, -111.796818, 730, 1500, "E/W"],
	["600 N", 41.743097, -111.859219, 41.742828, -111.839786, -1000, -200, "E/W"],
	["600 N", 41.742828, -111.839786, 41.742585, -111.834644, -200, 0, "E/W"],
	["600 N", 41.742926, -111.834659, 41.742597, -111.81672, 0, 700, "E/W"],
	["500 N", 41.741159, -111.849442, 41.740642, -111.816765, -600, 700, "E/W"],
	["400 N", 41.739251, -111.849529, 41.739252, -111.847549, -600, -500, "E/W"],
	["400 N", 41.739252, -111.847549, 41.738754, -111.816803, -500, 600, "E/W"],
	["US-89", 41.738754, -111.816803, 41.738602, -111.814958, 600, 675, "E/W"],
	["US-89", 41.738602, -111.814958, 41.740087, -111.810646, 675, 910, "E/W"],
	["US-89", 41.740087, -111.810646, 41.740963, -111.807201, 910, 1075, "E/W"],
	["US-89", 41.740963, -111.807201, 41.742528, -111.804282, 1075, 1200, "E/W"],
	["US-89", 41.742528, -111.804282, 41.743495, -111.802072, 1200, 1290, "E/W"],
	["US-89", 41.743495, -111.802072, 41.743911, -111.794702, 1290, 1590, "E/W"],
	["300 N", 41.737379, -111.849588, 41.737329, -111.847678, -600, -500, "E/W"],
	["300 N", 41.737329, -111.847678, 41.736918, -111.820343, -500, 565, "E/W"],
	["200 N", 41.736082, -111.888454, 41.735468, -111.8497, -2163, -600, "E/W"],
	["200 N", 41.735468, -111.8497, 41.735434, -111.847748, -600, -500, "E/W"],
	["200 N", 41.735434, -111.847748, 41.735031, -111.824573, -500, 400, "E/W"],
	["200 S", 41.728088, -111.859888, 41.727974, -111.849883, -1000, -600, "E/W"],
	["200 S", 41.727792, -111.849876, 41.727775, -111.847975, -600, -500, "E/W"],
	["200 S", 41.727775, -111.847975, 41.727665, -111.842858, -500, -300, "E/W"],
	["200 S", 41.727796, -111.837703, 41.727471, -111.820439, -100, 573, "E/W"],
	["400 S", 41.723951, -111.832656, 41.724259, -111.852501, 100, -667, "E/W"],
	["600 S", 41.720694, -111.859951, 41.720569, -111.851712, -1000, -640, "E/W"],
	["600 S", 41.720532, -111.843073, 41.720531, -111.839563, -300, -163, "E/W"],
	["600 S", 41.720531, -111.839563, 41.721173, -111.835263, -163, 0, "E/W"],
	["Three Pointe Ave", 41.723453, -111.853043, 41.723627, -111.860068, -700, -1000, "E/W"],
	["1000 S", 41.713377, -111.860212, 41.713339, -111.857471, -1000, -900, "E/W"],
	["1000 S", 41.713339, -111.857471, 41.713268, -111.852853, -900, -800, "E/W"],
	["1000 S", 41.713268, -111.852853, 41.713219, -111.848539, -800, -580, "E/W"],
	["1000 S", 41.713219, -111.848539, 41.714065, -111.847373, -580, -500, "E/W"],
	["Golf Course Rd", 41.714065, -111.847373, 41.71489, -111.846308, -500, -400, "E/W"],
	["Golf Course Rd", 41.71489, -111.846308, 41.714919, -111.844618, -400, -280, "E/W"],
	["Golf Course Rd", 41.714919, -111.844618, 41.716061, -111.840803, -280, -210, "E/W"],
	["Golf Course Rd", 41.716061, -111.840803, 41.716078, -111.839448, -210, -140, "E/W"],
	["Golf Course Rd", 41.716078, -111.839448, 41.715378, -111.838124, -140, -75, "E/W"],
	["Golf Course Rd", 41.715378, -111.838124, 41.715312, -111.836415, -75, 0, "E/W"],
	["1100 S", 41.71235, -111.839439, 41.711752, -111.83887, -100, -87, "E/W"],
	["1100 S", 41.711752, -111.83887, 41.710719, -111.838781, -87, -75, "E/W"],
	["1100 S", 41.710719, -111.838781, 41.710267, -111.838015, -75, -65, "E/W"],
	["1200 S", 41.710267, -111.838015, 41.710171, -111.831945, -65, 40, "E/W"],

# LOGAN, NORTH LOGAN NORTH/SOUTH STREETS
	["1000 W", 41.778019, -111.85842, 41.69699, -111.86032, 2500, -1960, "N/S"],
	["800 W", 41.713266, -111.852852, 41.705659, -111.853134, -1000, -1580, "N/S"],
	["800 W", 41.705659, -111.853134, 41.704244, -111.852724, -1580, -1640, "N/S"],
	["800 W", 41.704244, -111.852724, 41.703432, -111.851589, -1640, -1700, "N/S"],
	["600 W", 41.778019, -111.84879, 41.726716, -111.849947, 2500, -267, "N/S"],
	["600 W", 41.726716, -111.849947, 41.723462, -111.853078, -267, -430, "N/S"],
	["400 W", 41.766939, -111.843721, 41.752393, -111.844191, 1898, 1105, "N/S"],
	["400 W", 41.752393, -111.844191, 41.751875, -111.844742, 1105, 1085, "N/S"],
	["400 W", 41.751875, -111.844742, 41.723442, -111.845596, 1085, -437, "N/S"],
	["300 W", 41.741038, -111.84243, 41.720532, -111.843073, 500, -600, "N/S"],
	["300 W", 41.720528, -111.842453, 41.715559, -111.842521, -600, -876, "N/S"],
	["Park Ave", 41.723462, -111.853078, 41.719115, -111.853228, -430, -684, "N/S"],
	["Park Ave", 41.719115, -111.853228, 41.718248, -111.852747, -684, -720, "N/S"],
	["Park Ave", 41.718248, -111.852747, 41.713266, -111.852852, -720, -1000, "N/S"],
	["200 W", 41.772518, -111.838811, 41.729536, -111.840237, 2200, -100, "N/S"],
	["100 W", 41.746418, -111.836454, 41.744881, -111.836538, 800, 713, "N/S"],
	["100 W", 41.744881, -111.836538, 41.744056, -111.837228, 713, 670, "N/S"],
	["100 W", 41.744056, -111.837228, 41.722203, -111.837881, 670, -500, "N/S"],
	["100 W", 41.722203, -111.837881, 41.720775, -111.837919, -500, -600, "N/S"],
	["100 E", 41.7463, -111.831851, 41.721874, -111.832742, 800, -512, "N/S"],
	["100 E", 41.721874, -111.832742, 41.720323, -111.831412, -512, -664, "N/S"],
	["100 E", 41.720323, -111.831412, 41.718576, -111.831206, -664, -724, "N/S"],
	["100 E", 41.718576, -111.831206, 41.717481, -111.830018, -724, -770, "N/S"],
	["100 E", 41.717481, -111.830018, 41.716938, -111.830021, -770, -800, "N/S"],
	["Wolfpack Way", 41.787595, -111.829816, 41.786421, -111.829897, 3100, 3020, "N/S"],
	["Wolfpack Way", 41.786421, -111.829897, 41.784192, -111.830876, 3020, 2830, "N/S"],
	["Wolfpack Way", 41.784192, -111.830876, 41.776554, -111.830537, 2830, 2450, "N/S"],
	["Wolfpack Way", 41.776554, -111.830537, 41.773452, -111.828393, 2450, 2260, "N/S"],
	["200 E, North Logan", 41.773452, -111.828393, 41.759368, -111.828961, 2260, 1500, "N/S"],
	["200 E", 41.759368, -111.828961, 41.725832, -111.829971, 1500, -300, "N/S"],
	["Research Park Way, North Logan", 41.761215, -111.820703, 41.762169, -111.820276, 1600, 1650, "N/S"],
	["Research Park Way, North Logan", 41.761335, -111.820258, 41.762169, -111.820693, 1605, 1650, "N/S"],
	["Research Park Way, North Logan", 41.762475, -111.821306, 41.762892, -111.821394, 1650, 1670, "N/S"],
	["Research Park Way, North Logan", 41.762892, -111.821394, 41.763931, -111.820961, 1670, 1770, "N/S"],
	["Research Park Way, North Logan", 41.763931, -111.820961, 41.764914, -111.820893, 1770, 1800, "N/S"],
	["600 E", 41.777684, -111.818463, 41.734938, -111.819303, 2400, 200, "N/S"],
	["700 E", 41.744558, -111.815825, 41.743783, -111.816704, 700, 661, "N/S"],
	["700 E", 41.743783, -111.816704, 41.739249, -111.8168, 661, 428, "N/S"],
	["700 E", 41.744492, -111.816656, 41.750076, -111.816411, 700, 1000, "N/S"],
	["800 E, North Logan", 41.784067, -111.813083, 41.759421, -111.813859, 2900, 1500, "N/S"],
	["800 E", 41.759421, -111.813859, 41.743467, -111.8142, 1500, 635, "N/S"],
	["1200 E, North Logan", 41.772963, -111.804493, 41.758482, -111.804277, 2300, 1500, "N/S"],
	["1200 E", 41.758482, -111.804277, 41.742528, -111.804282, 1500, 600, "N/S"],
	["1500 E", 41.749416, -111.796765, 41.747546, -111.796783, 1000, 900, "N/S"],
	["1500 E", 41.747546, -111.796783, 41.743775, -111.796819, 900, 678, "N/S"],
	["1600 E", 41.760167, -111.794641, 41.748048, -111.79451, 1600, 920, "N/S"],

# Technically in Logan but between Providence (200 W) and Millville (Main)
	["400 E", 41.695996, -111.823229, 41.694797, -111.823272, -2020, -2100, "N/S"],

# PROVIDENCE
	["Gateway Dr, Providence", 41.716938, -111.830021, 41.714975, -111.830044, 435, 358, "N/S"],
	["Gateway Dr, Providence", 41.714975, -111.830044, 41.714332, -111.830294, 358, 320, "N/S"],
	["Gateway Dr, Providence", 41.714332, -111.830294, 41.713406, -111.830313, 320, 270, "N/S"],
	["Gateway Dr, Providence", 41.713406, -111.830313, 41.712121, -111.829137, 270, 210, "N/S"],
	["Gateway Dr, Providence", 41.712121, -111.829137, 41.710115, -111.829162, 210, 100, "N/S"],
	["Spring Creek Pkwy, Providence", 41.712419, -111.829377, 41.713592, -111.827730, 246, 280, "N/S"],
	["300 W, Providence", 41.713398, -111.825606, 41.710047, -111.825722, 280, 100, "N/S"],
	["200 W, Providence", 41.709976, -111.822772, 41.695996, -111.823229, 100, -620, "N/S"],
	["100 W, Providence", 41.715463, -111.820164, 41.698516, -111.820584, 392, -500, "N/S"],
	["Main Street, Providence", 41.711791, -111.817665, 41.696344, -111.818089, 200, -600, "N/S"],
	["280 N, Providence", 41.713592, -111.827730, 41.713432, -111.827178, -390, -358, "E/W"],
	["280 N, Providence", 41.713432, -111.827178, 41.713283, -111.820218, -358, -100, "E/W"],
	["200 N, Providence", 41.711852, -111.821337, 41.711609, -111.807578, -150, 400, "E/W"],
	["100 N, Providence", 41.710171, -111.831945, 41.709749, -111.807628, -560, 400, "E/W"],
	["Center Street, Providence", 41.708071, -111.822866, 41.707862, -111.81024, -200, 300, "E/W"],

# MILLVILLE
	["100 W, Millville", 41.688513, -111.826278, 41.676366, -111.826536, 400, -300, "N/S"],
	["Main Street, Millville", 41.694797, -111.823272, 41.689405, -111.823518, 730, 450, "N/S"],
	["Main Street, Millville", 41.689405, -111.823518, 41.676322, -111.823698, 450, -300, "N/S"],
	["100 S, Millville", 41.679803, -111.826445, 41.679726, -111.818068, -100, 200, "E/W"],
	["200 S, Millville", 41.677371, -111.83035, 41.678069, -111.827842, -300, -200, "E/W"],
	["200 S, Millville", 41.678069, -111.827842, 41.679803, -111.826445, -200, -100, "E/W"],
	["200 S, Millville", 41.678071, -111.826523, 41.677946, -111.815368, -100, 300, "E/W"],

# NIBLEY
	["Mill Rd, Nibley", 41.67668, -111.833360, 41.677371, -111.83035, 0, 200, "E/W"],

# HYRUM
	["Main Street, Hyrum", 41.634284, -111.866372, 41.633643, -111.835708, -400, 700, "E/W"],
	["Main Street, Hyrum", 41.633643, -111.835708, 41.633583, -111.831966, 700, 825, "E/W"],
	["400 N, Hyrum", 41.644353, -111.871455, 41.644198, -111.863087, -608, -300, "E/W"],
	["300 S, Hyrum", 41.628007, -111.866545, 41.627368, -111.835909, -400, 700, "E/W"],
	["300 S, Hyrum", 41.627368, -111.835909, 41.627311, -111.832612, 700, 800, "E/W"],
	["300 S, Hyrum", 41.627311, -111.832612, 41.62719, -111.813494, 800, 1600, "E/W"],
	["Blacksmith Fork Canyon Rd, Hyrum", 41.633583, -111.831966, 41.634353, -111.829014, 825, 945, "E/W"],
	["Blacksmith Fork Canyon Rd, Hyrum", 41.634353, -111.829014, 41.634372, -111.816345, 945, 1400, "E/W"],
	["400 W, Hyrum", 41.644249, -111.865813, 41.640532, -111.866017, 400, 300, "N/S"],
	["400 W, Hyrum", 41.640532, -111.866017, 41.628007, -111.866545, 300, -300, "N/S"],
	["200 W, Hyrum", 41.644198, -111.860931, 41.640411, -111.860491, 400, 300, "N/S"],
	["200 W, Hyrum", 41.640411, -111.860491, 41.625882, -111.860978, 300, -400, "N/S"],
	["Center St, Hyrum", 41.642603, -111.854845, 41.623759, -111.85557, 420, -500, "N/S"],
	["1300 E, Hyrum", 41.634375, -111.818927, 41.630378, -111.818963, 0, -150, "N/S"],
	["1300 E, Hyrum", 41.630378, -111.818963, 41.628654, -111.819844, -150, -250, "N/S"],
	["1300 E, Hyrum", 41.628654, -111.819844, 41.627176, -111.819857, -250, -300, "N/S"],
]

S_NAME = 0
S_BLAT = 1
S_BLON = 2
S_ELAT = 3
S_ELON = 4
S_BADDR = 5
S_EADDR = 6
S_DIR = 7

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
		[[41.74089, -111.830632,
			[41.74089, -111.830632, "150 E 500 N"]],
		[41.740884, -111.829543,
			[41.742988, -111.829461, "604 N 200 E"],
			[41.744929, -111.829449, "704 N 200 E"],
			[41.748844, -111.829353, "918 N 200 E"],
			[41.753042, -111.829203, "1206 N 200 E"],
			[41.756348, -111.829114, "1360 N 200 E"]],
		[41.757472, -111.829075,
			[41.75748, -111.826417, "330 E 1400 N"],
			[41.75746, -111.822197, "465 E 1400 N"]],
		[41.757406, -111.819011,
			[41.760497, -111.818968, "1500 N 600 E"]],
		[41.762147, -111.818947],
		[41.762181, -111.820783],
		[41.762577, -111.821362],
		[41.762937, -111.821385,
			[41.763569, -111.821092, "1750 N Research Park Way"]],
		[41.763936, -111.820965],
		[41.764915, -111.820889,
			[41.764881, -111.819167, "1800 N 600 E"]],
		[41.764803, -111.81368,
			[41.763819, -111.813734, "1775 N 800 E"],
			[41.759013, -111.813862, "1521 N 800 E"],
			[41.756687, -111.813822, "1380 N 800 E"],
			[41.753351, -111.813889, "1200 N 800 E"],
			[41.751704, -111.813895, "1111 N 800 E"]],
		[41.750145, -111.813885],
		[41.750157, -111.815864],
		[41.749925, -111.816991,
			[41.749925, -111.816991, "695 East 1000 North"]],
		[41.749885, -111.819028],
		[41.750647, -111.819258,
			[41.751199, -111.819264, "1090 N 600 E"],
			[41.755687, -111.819079, "1320 N 600 E"]],
		[41.757406, -111.819011,
			[41.75742, -111.820473, "545 E 1400 N"],
			[41.757475, -111.826113, "330 E 1400 N"]],
		[41.757472, -111.829075,
			[41.7562, -111.829126, "1365 N 200 E"],
			[41.75282, -111.829217, "1201 N 200 E"],
			[41.749657, -111.829325, "979 N 200 E"]],
		[41.744683, -111.829461,
			[41.744699, -111.830507, "165 E 700 N"]],
		[41.744686, -111.831879],
		[41.740912, -111.832032],]
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

def sub_proj_ratio(lat, lon, blat, blon, elat, elon):
	blat_diff = lat-blat
	blon_diff = lon-blon
	elat_diff = lat-elat
	elon_diff = lon-elon

	st_begin_dist = math.sqrt(blat_diff * blat_diff + blon_diff * blon_diff)
	st_end_dist = math.sqrt(elat_diff * elat_diff + elon_diff * elon_diff)

	if st_begin_dist > st_end_dist:
		street_lat = elat - blat
		street_lon = elon - blon
		pos_lat = lat - blat
		pos_lon = lon - blon
		begin_or_end = 1
	else:
		street_lat = blat - elat
		street_lon = blon - elon
		pos_lat = lat - elat
		pos_lon = lon - elon
		begin_or_end = 0

	street_sc = math.sqrt(street_lat * street_lat + street_lon * street_lon)
	pos_sc =  math.sqrt(pos_lat * pos_lat + pos_lon * pos_lon)
	projection_sc = ((pos_lat * street_lat) + (pos_lon * street_lon)) / ((street_lat * street_lat) + (street_lon * street_lon)) * street_sc

	return street_sc, pos_sc, projection_sc, begin_or_end

# Returns street index
#         projection ratio, where 0 is the beginning and 1 is the end
#         scalar error
def compute_proj_ratio(lat, lon, valid_streets):
	min_pos_to_proj = 0x7FFFFFFF
	min_proj_ratio = 0
	min_street_ix = 0

	for street_ix, street in enumerate(ROAD_LIST):
		if valid_streets is None or street_ix in valid_streets:
			blat = street[S_BLAT]
			blon = street[S_BLON]
			elat = street[S_ELAT]
			elon = street[S_ELON]
			street_sc, pos_sc, projection_sc, begin_or_end = sub_proj_ratio(lat, lon, blat, blon, elat, elon)

			proj_sc_fixed = min(projection_sc, street_sc)
			pos_to_proj = math.sqrt((pos_sc * pos_sc) - (proj_sc_fixed * proj_sc_fixed))

			if pos_to_proj < min_pos_to_proj:
				min_pos_to_proj = pos_to_proj
				min_proj_ratio = projection_sc / street_sc
				min_street_ix = street_ix

				if begin_or_end == 0:
					min_proj_ratio = 1 - min_proj_ratio

	return min_street_ix, min_proj_ratio, min_pos_to_proj

def compute_addr(lat, lon, valid_streets):
	ix, proj_ratio, error = compute_proj_ratio(lat, lon, valid_streets)

	vaddr_begin = ROAD_LIST[ix][S_BADDR]
	vaddr_end = ROAD_LIST[ix][S_EADDR]

	address = round(proj_ratio * (vaddr_end - vaddr_begin) + vaddr_begin)
	if ROAD_LIST[ix][S_DIR] == "N/S":
		if address > 0:
			nesw = "N"
		else:
			nesw = "S"
	elif ROAD_LIST[ix][S_DIR] == "E/W":
		if address > 0:
			nesw = "E"
		else:
			nesw = "W"
	else:
		nesw = ROAD_LIST[ix][S_DIR]

	return "{} {} {}".format(abs(address), nesw, ROAD_LIST[ix][S_NAME]), error*70*5280

# Assume segment percent is a number between 0 and 1
def compute_route_completion(points, segment_ix, segment_percent):
	distances = []
	for ix, segment in enumerate(points):
		blat1 = ROAD_LIST[segment[0]][S_BLAT]
		blon1 = ROAD_LIST[segment[0]][S_BLON]
		elat1 = ROAD_LIST[segment[0]][S_ELAT]
		elon1 = ROAD_LIST[segment[0]][S_ELON]
		dlat1 = abs(elat1 - blat1)
		dlon1 = abs(elon1 - blon1)

		nsegment = points[ix + 1 if (ix + 1) < len(points) else 0]
		blat2 = ROAD_LIST[nsegment[0]][S_BLAT]
		blon2 = ROAD_LIST[nsegment[0]][S_BLON]
		elat2 = ROAD_LIST[nsegment[0]][S_ELAT]
		elon2 = ROAD_LIST[nsegment[0]][S_ELON]
		dlat2 = abs(elat2 - blat2)
		dlon2 = abs(elon2 - blon2)

		if segment[0] == nsegment[0]:
			# Great, we're measuring distance between two points on the same road
			this_lat = (nsegment[1] - segment[1]) * dlat1
			this_lon = (nsegment[1] - segment[1]) * dlon1
			distance = math.sqrt(this_lat * this_lat + this_lon * this_lon)
			distances.append(distance)
		else:
			# Sum the distance travelled on the two segments
			this_lat = (1 - segment[1]) * dlat1
			this_lon = (1 - segment[1]) * dlon1
			distance1 = math.sqrt(this_lat * this_lat + this_lon * this_lon)

			this_lat = nsegment[1] * dlat1
			this_lon = nsegment[1] * dlon1
			distance2 = math.sqrt(this_lat * this_lat + this_lon * this_lon)

			distance = distance1 + distance2
			distances.append(distance)

	total_distance = sum(distances)
	distance_travelled = sum(distances[:segment_ix]) + (segment_percent * distances[segment_ix])
	return distance_travelled / total_distance

def routefix(route):
	points = route
	result = ''

	# First, generate the points
	result = '['
	stops_result = ''
	s = '['
	for p_ix, p in enumerate(points):
		ix, proj_ratio, error = compute_proj_ratio(p[0], p[1], None)

		p_next_ix = (p_ix + 1) % len(points);

		heading = round(math.degrees(math.atan2(points[p_next_ix][1] - p[1], points[p_next_ix][0] - p[0])))
		s = s + '[' + str(ix) + ", " + str(round(proj_ratio, 6)) + ', ' + str(heading) + '],'
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

def datadrop(route):
	route_fixed = eval(routefix(route))
	valid_streets = set(a[0] for a in route_fixed[0])
	for d in DATA_DROP:
		print("{: <16}{: <16}{}".format(d[1], d[2], compute_addr(d[3], d[4], valid_streets)[0]))

def get_direction(d):
	the_dict = {0: "N", 45: "NE", 90: "E", 135: "SE", 180: "S", 225: "SW", 270: "W", 315: "NW", 360: "N"}
	d = round(d / 45) * 45
	return the_dict[d]

def pull():
	with open('key.txt', 'r') as f:
		key = f.read()
	os.system("curl -o cvtddata.txt http://cvtd.info:8080/CVTDfeed/V200/XML/_System.php?key={}".format(key))
	tree = ET.parse('cvtddata.txt')
	root = tree.getroot()
	for bus in root:
		try:
			route = bus[5].text
			lat = float(bus[8][0][0].text)
			lon = float(bus[8][0][1].text)
			direction = int(bus[8][0][2].text)
			addr, error = compute_addr(lat, lon, None)
			error = round(error)
			pos_to_pos_diff = abs((float(bus[8][1][0].text) - lat))*70*5280
			if (direction == 0) and (pos_to_pos_diff < 40):
				direction = 'STOPPED'
			else:
				direction = get_direction(direction)
			print("{: <20}{: <40}{: <10}{}".format(route, addr, str(error) + " feet", direction))
		except IndexError:
			pass

def main():
	while True:
		text_in = input(">>> ")
		text_spl = text_in.strip().split()
		if len(text_in) == 0:
			continue
		if text_in.lower() in ['exit', 'e', 'exit()', 'quit', 'q']:
			break
		elif text_in.lower() in ['help', 'usage', 'h', 'u']:
			print("{: <24}Bring up this help page".format("help"))
			print("{: <24}Quits the app".format("quit"))
			print("{: <24}Computes an address for the provided latitude and longitude".format("addr [lat] [lon]"))
			print("{: <24}Converts a route from latitude and longitude to street and proj ratio".format("routefix [route]"))
			print("{: <24}Prints address and route completion for data drop for given route".format("datadrop [route]"))
			print("{: <24}Prints percent complete for given point of given route".format("ppt [route] [pointix]"))
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
				print("Error [ppt]: Please provide the name of the route and the index of the point")
			except KeyError:
				print("Error [ppt]: Route {} does not exist".format(text_spl[1]))
			except ValueError:
				print("Error [ppt]: Point {} could not be converted to an integer".format(text_spl[2]))
		elif text_spl[0].lower() == 'pull':
			pull()

		print("")

if __name__ == '__main__':
	main()