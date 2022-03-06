import datetime

from cvtdBus import CvtdBus
from cvtdNode import CvtdNode
from cvtdUtil import CvtdUtil
from gtfsCalendarEntry import GtfsCalendarEntry
from gtfsShape import GtfsShape
from gtfsStop import GtfsStop
from gtfsStopTime import GtfsStopTime
from gtfsTrip import GtfsTrip

####
# "Static" class to import Google Transit files
####
class GtfsImporter:
  ####
  # import_calendar imports calendar entries into myMap.
  #
  # dirPath is the path to the directory containing Google Transit files
  # mainMap is the CvtdMap that calendar will be written to
  ####
  def import_calendar(dirPath, myMap):
    print("Importing calendar...")
    calendarDict = {}
    calendar = CvtdUtil.parse_csv(dirPath + "/calendar.txt")
    strFormat = '%Y%m%d'
    try:
      for ix, sid in enumerate(calendar['service_id']):
        if sid not in calendarDict:
          calendarDict[sid] = GtfsCalendarEntry()
        monday = int(calendar['monday'][ix])
        tuesday = int(calendar['tuesday'][ix])
        wednesday = int(calendar['wednesday'][ix])
        thursday = int(calendar['thursday'][ix])
        friday = int(calendar['friday'][ix])
        saturday = int(calendar['saturday'][ix])
        sunday = int(calendar['sunday'][ix])
        calendarDict[sid].generateDaysOfWeek(monday, tuesday, wednesday, thursday, friday, saturday, sunday)
        calendarDict[sid].startDate = datetime.datetime.strptime(calendar['start_date'][ix], strFormat)
        calendarDict[sid].endDate = datetime.datetime.strptime(calendar['end_date'][ix], strFormat)
    except (KeyError, IndexError, ValueError):
      print(f"Error: import_calendar, ix {ix}, sid {sid}")
      pass
  
    myMap.calendarDict = calendarDict

  ####
  # import_routes imports routes into myMap.
  #
  # dirPath is the path to the directory containing Google Transit files
  # mainMap is the CvtdMap that routes will be written to
  ####
  def import_routes(dirPath, myMap):
    print("Importing routes...")
    routeDict = {}
    routes = CvtdUtil.parse_csv(dirPath + "/routes.txt")
    try:
      for ix, rid in enumerate(routes['route_id']):
        if rid not in routeDict:
          routeDict[rid] = GtfsStop()

        routeDict[rid].agencyId = routes['agency_id'][ix]
        routeDict[rid].routeShortName = routes['route_short_name'][ix]
        routeDict[rid].routeLongName = routes['route_long_name'][ix]
        routeDict[rid].routeDesc = routes['route_desc'][ix]
        routeDict[rid].routeType = int(routes['route_type'][ix])
    except (KeyError, IndexError, ValueError):
      print(f"Error: import_routes, ix {ix}, rid {rid}")
      pass
  
    myMap.routeDict = routeDict

  ####
  # import_shapes imports shapes and tries to combine identical ones into the same bucket
  #
  # dirPath is the path to the directory containing Google Transit files
  # mainMap is the CvtdMap that roads and nodes will be merged into
  ####
  def import_shapes(dirPath, myMap):
    print("Importing shapes...")
    shapeDict = {}
    shapes = CvtdUtil.parse_csv(dirPath + "/shapes.txt")
    try:
      for ix, sid in enumerate(shapes['shape_id']):
        if sid not in shapeDict:
          shapeDict[sid] = GtfsShape()
        lat = float(shapes['shape_pt_lat'][ix])
        lon = float(shapes['shape_pt_lon'][ix])
        shapeDict[sid].pointList.append(CvtdNode(lat, lon))
    except (KeyError, IndexError, ValueError):
      print(f"Error: import_shapes, ix {ix}, sid {sid}")
      pass
  
    for shapeId in shapeDict:
      for cmpShapeId in shapeDict:
        if shapeId != cmpShapeId:
          if shapeDict[shapeId].copyOfId is None and shapeDict[cmpShapeId].copyOfId is None:
            if shapeDict[shapeId].compare_point_list(shapeDict[cmpShapeId].pointList):
              shapeDict[cmpShapeId].pointList = []
              shapeDict[cmpShapeId].copyOfId = shapeId
              print(f"Shape {cmpShapeId} is a copy of {shapeId}")
    myMap.shapeDict = shapeDict

  ####
  # import_stops imports stops into myMap.
  #
  # dirPath is the path to the directory containing Google Transit files
  # mainMap is the CvtdMap that stops will be written to
  ####
  def import_stops(dirPath, myMap):
    print("Importing stops...")
    stopDict = {}
    stops = CvtdUtil.parse_csv(dirPath + "/stops.txt")
    try:
      for ix, sid in enumerate(stops['stop_id']):
        if sid not in stopDict:
          stopDict[sid] = GtfsStop()

        if stops['stop_code'][ix] is not '':
          stopDict[sid].stopCode = int(stops['stop_code'][ix])
        stopDict[sid].stopName = stops['stop_name'][ix]
        stopDict[sid].lat = float(stops['stop_lat'][ix])
        stopDict[sid].lon = float(stops['stop_lon'][ix])
        if stops['location_type'][ix] is not '':
          stopDict[sid].locationType = int(stops['location_type'][ix])
        if stops['parent_station'][ix] is not '':
          stopDict[sid].parentStation = int(stops['parent_station'][ix])
    except (KeyError, IndexError, ValueError):
      print(f"Error: import_stops, ix {ix}, sid {sid}")
      pass
  
    myMap.stopDict = stopDict

  ####
  # import_stop_times imports stop times into myMap.
  #
  # dirPath is the path to the directory containing Google Transit files
  # mainMap is the CvtdMap that stop times will be written to
  ####
  def import_stop_times(dirPath, myMap):
    print("Importing stop times...")
    stopTimeDict = {}
    stopTimes = CvtdUtil.parse_csv(dirPath + "/stop_times.txt")
    try:
      for ix, tid in enumerate(stopTimes['trip_id']):
        sid = stopTimes['stop_id'][ix]
        if (tid, sid) not in stopTimeDict:
          stopTimeDict[(tid, sid)] = GtfsStopTime()
        stopTimeDict[(tid, sid)].departure = datetime.datetime.strptime(stopTimes['departure_time'][ix], "%H:%M:%S").time()
        stopTimeDict[(tid, sid)].arrival = datetime.datetime.strptime(stopTimes['arrival_time'][ix], "%H:%M:%S").time()
        stopTimeDict[(tid, sid)].timepoint = stopTimes['timepoint'][ix] == '1'
    except (KeyError, IndexError, ValueError):
      print(f"Error: import_stop_times, ix {ix}, tid {tid}, sid {sid}")
      pass
  
    myMap.stopTimeDict = stopTimeDict

  ####
  # import_trips imports trips into myMap.
  #
  # dirPath is the path to the directory containing Google Transit files
  # mainMap is the CvtdMap that trips will be written to
  ####
  def import_trips(dirPath, myMap):
    print("Importing trips...")
    tripDict = {}
    trips = CvtdUtil.parse_csv(dirPath + "/trips.txt")
    try:
      for ix, tid in enumerate(trips['trip_id']):
        if tid not in tripDict:
          tripDict[tid] = GtfsTrip()
        tripDict[tid].routeId = trips['route_id'][ix]
        tripDict[tid].serviceId = trips['service_id'][ix]
        tripDict[tid].directionId = int(trips['direction_id'][ix])
        tripDict[tid].blockId = trips['block_id'][ix].replace('"', '')
        tripDict[tid].shapeId = int(trips['shape_id'][ix])
    except (KeyError, IndexError, ValueError):
      print(f"Error: import_trips, ix {ix}, tid {tid}")
      pass
  
    myMap.tripDict = tripDict

  ####
  # generate_osm_query generates a text-based OSM query based on shapes.txt
  #
  # filename is the path to where the Bash script should be written to
  # myMap is the map after the shapes have been imported
  ####
  def generate_osm_query(filename, myMap):
    LATDIFF = 0.02
    LONDIFF = 0.02

    buckets = set()
    for shapeKey in myMap.shapeDict:
      for point in myMap.shapeDict[shapeKey].pointList:
        minLat = int(point.lat / LATDIFF) * LATDIFF
        minLon = int(point.lon / LONDIFF) * LONDIFF
        buckets.add((minLat, minLon))
    buckets = list(buckets)
    buckets.sort(key=lambda a: a[1])
    buckets.sort(key=lambda a: a[0])
    
    # Generate the bash script
    with open(filename, 'w') as f:
      for bucket in buckets:
        s1 = "wget -O Logan_{}{}_{}{}_{}{}_{}{}".format(
          int(bucket[0]),
          str(round(abs(bucket[0] - int(bucket[0])), 6))[2:],
          int(bucket[0] + LATDIFF),
          str(round(abs((bucket[0] + LATDIFF) - int((bucket[0] + LATDIFF))), 6))[2:],
          int(bucket[1]),
          str(round(abs(bucket[1] - int(bucket[1])), 6))[2:],
          int(bucket[1] + LONDIFF),
          str(round(abs((bucket[1] + LONDIFF) - int((bucket[1] + LONDIFF))), 6))[2:],
        )
        s2 = '.osm "https://overpass-api.de/api/interpreter?nwr'
        s3 = '({},{},{},{});out;"\n'.format(
          round(bucket[0], 6),
          round(bucket[1], 6),
          round(bucket[0] + LATDIFF, 6),
          round(bucket[1] + LONDIFF, 6)
        )
        f.write(s1 + s2 + s3)
        f.write("sleep 10\n")

  ####
  # Application entry point for importing Google Transit files
  #
  # dirPath is the path to the directory containing Google Transit Feed Specification files
  # mainMap is the CvtdMap that roads and nodes will be merged into
  ####
  def import_google_directory(dirPath, myMap):
    GtfsImporter.import_calendar(dirPath, myMap)
    GtfsImporter.import_routes(dirPath, myMap)
    GtfsImporter.import_shapes(dirPath, myMap)
    GtfsImporter.import_stop_times(dirPath, myMap)
    GtfsImporter.import_stops(dirPath, myMap)
    GtfsImporter.import_trips(dirPath, myMap)
    GtfsImporter.generate_osm_query("osmquery.sh", myMap)
