#!/usr/bin/python3
import os
import random
import sys
import xml.etree.ElementTree as ET

from cvtdNode import CvtdNode
from cvtdRoad import CvtdRoad
from cvtdRoadPoint import CvtdRoadPoint
from cvtdMap import CvtdMap
from cvtdUtil import CvtdUtil
from gtfsImporter import GtfsImporter

HIGHWAY_BIGNESS = {
  "motorway"    : 50,
  "trunk"       : 30,
  "primary"     : 20,
  "secondary"   : 15,
  "tertiary"    : 10,
  "unclassified": 8,
  "residential" : 5,
}

####
# Application to import an XML file
#
# nodeDict is a dictionary, where the key is the XML ID and the value is a CvtdNode
# roadList is a list of CvtdRoad's, with 'addr' field set to None
# mainMap is the CvtdMap we will be merging into
####
class Importer:
  def __init__(self):
    self.roadList = []
    self.nodeDict = {}
    self.mainMap = None

  ####
  # Shows the options available to the user on the command line
  ####
  def show_help(self):
    print("")
    print("(1) Search for a road with the following name")
    print("(2) Extend existing roads")
    print("(3) Select most interesting new road")
    print("(q) Quit")

  ####
  # add_road helps the user to merge a road into the main map
  #
  # way is the index into self.roadList for the CvtdRoad to merge into
  # baseRoad is an index into self.mainMap.roadList, which is copied to become the new road, or None
  #
  # returns the indices of all roads that were added, or None if none were added
  ####
  def add_road(self, wayIx, baseRoadIx):
    way = self.roadList[wayIx]
    addedRoads = [wayIx]
    newRoad = CvtdRoad()
    if baseRoadIx is not None:
      # If we're appending onto a road, add all the nodes from the main map into this map
      baseRoad = self.mainMap.roadList[baseRoadIx]
      newRoad.name = baseRoad.name
      newRoad.dir = baseRoad.dir
      for point in baseRoad.points:
        self.nodeDict[point.node] = self.mainMap.nodeDict[point.node]
        newRoad.points.append(CvtdRoadPoint(point.node, point.addr))

    print(f"{way.name} goes from {self.nodeDict[way.points[0].node]} to {self.nodeDict[way.points[-1].node]} with {len(way.points)} points")

    newName = input(f'Enter a name for this road (leave blank for "{way.name}"): ')
    if newName:
      newRoad.name = newName
    else:
      newRoad.name = way.name
    newRoad.dir = input(f"Enter a direction for {newRoad.name} ('N/S', 'E/W', or other): ")
    minValue = None
    maxValue = None
    lastValue = None

    # Merge check, only once, at the end. Reset to True if they accept the merge
    mergeCheck = True

    # For each point in this way
    pointList = way.points
    # Let them come back to some points if desired
    while len(pointList) > 0:
      returnPointList = []
      for point in pointList:
        # Don't let the same point get added twice
        if point.node in [p.node for p in newRoad.points]:
          continue
        
        # Store the node in question
        node = self.nodeDict[point.node]

        # Look for ways in the OSM file that also use this node
        newIntersections = []
        for checkWay in self.roadList:
          if point.node in [checkPoint.node for checkPoint in checkWay.points]:
            newIntersections.append(checkWay)
        
        # Calculate the "best guess" for the address at this point
        interpolateAddress = newRoad.estimate_addr(node, self.nodeDict)
        print(f"\nNext point is ({node.lat}, {node.lon}), best guess {interpolateAddress}")
        if len(newIntersections) > 0:
          print(f"The following {len(newIntersections)} roads from the OSM file intersect at this node: ")
          for way in newIntersections:
            print(" - " + way.name + ': ' + str(way.tags))

        # Determine a max and a min value for this point
        if len(newRoad.points) == 0:
          minValue = None
          maxValue = None
          neValue = None
        elif len(newRoad.points) == 1:
          minValue = None
          maxValue = None
          neValue = newRoad.points[0].addr
        else:
          point_ix, proj_ratio, error = newRoad.compute_proj_ratio(node.lat, node.lon, self.nodeDict)
          inc = newRoad.increasing()
          if (proj_ratio < 0 and inc) or (proj_ratio > 1 and not inc):
            # Address must be less than the first address
            minValue = None
            maxValue = newRoad.points[0].addr - 1
            neValue = None
          elif (proj_ratio > 1 and inc) or (proj_ratio < 0 and not inc):
            # Address must be greater than the final address
            minValue = newRoad.points[-1].addr + 1
            maxValue = None
            neValue = None
          else:
            # Address must be between point #point_ix and the following point
            minValue = newRoad.points[point_ix].addr + 1 if inc else newRoad.points[point_ix + 1].addr - 1
            maxValue = newRoad.points[point_ix + 1].addr - 1 if inc else newRoad.points[point_ix].addr + 1
            neValue = None
          
        # Now let them choose an address, or 'skip' (ignore this point), or 'return' (come back to this point later)
        repeatThisAddr = True
        while repeatThisAddr:
          repeatThisAddr = False
          addr = CvtdUtil.input_int("Enter the address for this point, or 'skip', 'return' or 'edit': ", minValue, maxValue, neValue, ['skip', 'return', 'edit', 'quit', 's', 'r', 'e', 'q'])
          if addr is not None:
            if addr in ["skip", 's']:
              pass
            elif addr in ["return", 'r']:
              returnPointList.append(point)
            elif addr in ["edit", 'e']:
              newRoad.edit(self.nodeDict)
              repeatThisAddr = True
            elif addr in ["quit", 'q']:
              return
            else:
              newRoad.insert(CvtdRoadPoint(point.node, addr))
              newRoad.describe(self.nodeDict)
          else:
            return
      
      if len(returnPointList) > 0:
        pointList = returnPointList
      elif mergeCheck:
        pointList = []
        mergeCheck = False
        print("\nYou've defined the following road:")
        newRoad.describe(self.nodeDict)
        print('')

        # They successfully added all the points. See if they want to merge with another road
        possibleMerges = [way for way in self.roadList if newRoad.extendable(way)]

        if len(possibleMerges) > 0:
          print(f"There are {len(possibleMerges)} ways that you could merge into this road. ")
          for ix, way in enumerate(possibleMerges):
            print(f"[{ix+1}]: {way.name} has {len(way.points)} nodes")
            print(" " + ", ".join([f"({self.nodeDict[p.node].lat}, {self.nodeDict[p.node].lon})" for p in way.points]))
          
          mergeWay = CvtdUtil.input_int(f"Merge another road into this road? (1-{len(possibleMerges)}) or (n)o: ", 1, len(possibleMerges), validAnswers=['n', 'no'])
          if type(mergeWay) is int:
            mergeWay = mergeWay - 1
            pointList = possibleMerges[mergeWay].points
            addedRoads.append(self.roadList.index(possibleMerges[mergeWay]))
            mergeCheck = True
      else:
        # They were offered a merge check but they rejected it
        pointList = []

    confirm = 'e'
    while confirm == 'e':
      confirm = input("Add this new road to your map? (y/n/[e]dit): ")
      if confirm == 'e':
        newRoad.edit(self.nodeDict)
        print("\nYou've defined the following road:")
        newRoad.describe(self.nodeDict)
        print('')
      elif confirm == 'y':
        # If we are replacing a street (adding onto one), replace. Else add
        import pdb; pdb.set_trace()
        if baseRoadIx is not None:
          self.mainMap.replace_street_with_nodes(newRoad, self.nodeDict, baseRoadIx)
        else:
          self.mainMap.add_street_with_nodes(newRoad, self.nodeDict)
        print(f"You now have {len(self.mainMap.roadList)} roads.")

        # Remove each road, adjusting other indices for each road removed
        for ixOfIx, ixToRemove in enumerate(addedRoads):
          # Delete the ixToRemove'th index in self.roadList
          del self.roadList[ixToRemove]
          # Decrement all successive indices that are greater than ixToRemove
          for ixOfAdjustIx, ixToAdjust in enumerate(addedRoads[ixOfIx+1:]):
            if ixToAdjust > ixToRemove:
              addedRoads[ixOfAdjustIx] = addedRoads[ixOfAdjustIx] - 1
        return addedRoads

  ####
  # search_road searches for roads that match the given name, and helps the user to merge them in the main map
  ####
  def search_road(self):
    search = input("Search for a road with the following text: ")
    roadIxList = [i for i in range(len(self.roadList)) if search in self.roadList[i].name]
    ways = [self.roadList[way] for way in roadIxList]
    # ways = [way for way in self.roadList if search in way.name]

    if len(roadIxList) == 0:
      print("No ways found.")
      return

    # Print information about each of the matching ways
    for ix, way in enumerate(ways):
      try:
        print(f"[{ix+1}]: {way.name} has {len(way.points)} nodes")
        print(" " + ", ".join([f"({self.nodeDict[p.node].lat}, {self.nodeDict[p.node].lon})" for p in way.points]))
      except KeyError:
        print(f"Unknown node")
    
    # Here, compare with what is currently in the file to see if we want to add onto a road, modify a road, or do nothing
    # For the present, we'll just add a new road
    whichWay = CvtdUtil.input_int("Adding a new road. Start with which way? ", 1, len(ways))
    if type(whichWay) is int:
      self.add_road(roadIxList[whichWay - 1], None)
  
  ####
  # get_gtfs_location queries the user for the GTFS folder until they give up or provide a valid folder
  ####
  def get_gtfs_location(self):
    if self.mainMap.gtfsLocation == None:
      keepTrying = True
      while keepTrying:
        tryLocation = input("Please enter the path to the GTFS folder: ")
        if os.path.isdir(tryLocation):
          self.mainMap.gtfsLocation = tryLocation
          GtfsImporter.import_google_directory(tryLocation, self.mainMap)
          keepTrying = False
        else:
          keepTrying = input("That wasn't a valid folder location. Try again? (y/n) ")
  
  ####
  # generate_score_list calculates an "interesting" score for each road and returns the list
  #
  # roadIxList is one of the following:
  #  (a) a list of indices into self.roadList of roads that we are considering
  #  (b) a list of 2-tuples, where [0] is an index into self.roadList
  #                            and [1] is an index into self.mainMap.roadList
  #
  # return is a list of 2- or 3-tuples, where the first is the index of the road (in the main list)
  #  and the second is the score
  #  If (b) was passed in for roadIxList, the third is the index into self.mainMap.roadList
  ####
  def generate_score_list(self, roadIxList):
    self.get_gtfs_location()
    print("Generating score list...")
    if self.mainMap.gtfsLocation is not None:
      scoreList = []

      for roadIx in roadIxList:
        if type(roadIx) is tuple:
          mapRoadIx = roadIx[1]
          roadIx = roadIx[0]
        else:
          mapRoadIx = None
        road = self.roadList[roadIx]
        minErrorThisRoad = 0x7FFFFFFF
        ltOneFiftyCount = 0
        try:
          bignessScore = HIGHWAY_BIGNESS[road.tags["highway"]]
        except KeyError:
          bignessScore = 1
        for shapeKey in self.mainMap.shapeDict:
          # See how many points on this road fall within 150 ft of a segment on this shape
          shape = self.mainMap.shapeDict[shapeKey]
          for point in road.points:
            try:
              node = self.nodeDict[point.node]
            except KeyError:
              node = self.mainMap.nodeDict[point.node]
            minError = shape.get_min_point_error(node.lat, node.lon)
            if minError < minErrorThisRoad:
              minErrorThisRoad = minError
            if minError < 150:
              ltOneFiftyCount = ltOneFiftyCount + 1
        if mapRoadIx is not None:
          scoreList.append([roadIx, ltOneFiftyCount * bignessScore, mapRoadIx])
        else:
          scoreList.append([roadIx, ltOneFiftyCount * bignessScore])

      # Now sort by score
      scoreList.sort(key=lambda x: x[1], reverse=True)
      return scoreList
    return None
  
  ####
  # extend_existing_roads searches for the most interesting road to add and helps the user add it
  ####
  def extend_existing_roads(self):
    # Filter out all roads that have no name
    roadIxList = [i for i in range(len(self.roadList)) if self.roadList[i].name is not '']
    overlapRoadIxList = []

    if self.mainMap is not None:
      # Filter out all roads that don't overlap with a score of 4
      for roadIx in roadIxList:
        osmRoad = self.roadList[roadIx]
        for mapRoadIx, mapRoad in enumerate(self.mainMap.roadList):
          if osmRoad.compare_road(self.nodeDict, mapRoad, self.mainMap.nodeDict) == 4:
            overlapRoadIxList.append((roadIx, mapRoadIx))

    # Now generate a score list
    scoreList = self.generate_score_list(overlapRoadIxList)
    if scoreList:
      ix = 0
      while True:
        try:
          for i in range(5):
            p1 = self.mainMap.roadList[scoreList[i+ix][2]].name
            p2 = len(self.mainMap.roadList[scoreList[i+ix][2]].points)
            p3 = self.roadList[scoreList[i+ix][0]].name
            p4 = len(self.roadList[scoreList[i+ix][0]].points)
            print(f"{p1} ({p2} nodes) overlaps with {p3} ({p4} nodes) with score of {scoreList[i+ix][1]}")
        except IndexError:
          pass

        addRoad = input(f"Extend most interesting road: {self.roadList[scoreList[ix][0]].name}? (y/n/[s]kip) ")
        if addRoad == 'y':
          print('')
          ixes = self.add_road(scoreList[ix][0], scoreList[ix][2])

          # If the road was added, we get a list of any additional roads that were added
          # For each road added, adjust affected indices
          if ixes:
            for ixRemoved in ixes:
              # Adjust indices affected by this remove, which is any with a greater index
              # First, delete the error list entry with the index that was removed
              for errorListEntry in scoreList:
                if errorListEntry[0] == ixRemoved:
                  scoreList.remove(errorListEntry)
                  break
              # Now, adjust any indices
              for errorListEntry in scoreList:
                if errorListEntry[0] > ixRemoved:
                  errorListEntry[0] = errorListEntry[0] - 1
        elif addRoad == 's':
          ix = ix + 1
        elif addRoad == 'n':
          break
        else:
          print("I didn't understand that.")

  ####
  # add_most_interesting_road searches for the most interesting road to add and helps the user add it
  ####
  def add_most_interesting_road(self):
    # Filter out all roads that have no name
    roadIxList = [i for i in range(len(self.roadList)) if self.roadList[i].name is not '']

    scoreList = self.generate_score_list(roadIxList)
    if scoreList:
      # Now add roads as long as we desire
      ix = 0
      while True:
        try:
          for i in range(5):
            print(f"{self.roadList[scoreList[i+ix][0]].name} has score of {scoreList[i+ix][1]}")
        except IndexError:
          pass

        addRoad = input(f"Add most interesting road: {self.roadList[scoreList[ix][0]].name}? (y/n/[s]kip) ")
        if addRoad == 'y':
          print('')
          ixes = self.add_road(scoreList[ix][0], None)

          # If the road was added, we get a list of any additional roads that were added
          # For each road added, adjust affected indices
          if ixes:
            for ixRemoved in ixes:
              # Adjust indices affected by this remove, which is any with a greater index
              # First, delete the error list entry with the index that was removed
              for errorListEntry in scoreList:
                if errorListEntry[0] == ixRemoved:
                  scoreList.remove(errorListEntry)
                  break
              # Now, adjust any indices
              for errorListEntry in scoreList:
                if errorListEntry[0] > ixRemoved:
                  errorListEntry[0] = errorListEntry[0] - 1
        elif addRoad == 's':
          ix = ix + 1
        elif addRoad == 'n':
          break
        else:
          print("I didn't understand that.")

  ####
  # main function as seen by the user
  ####
  def main(self):
    command = "help"
    while command not in ["quit", "exit", "q", "e"]:
      if command == "1":
        self.search_road()
      elif command == "2":
        self.extend_existing_roads()
      elif command == "3":
        self.add_most_interesting_road()
      self.show_help()
      command = input("\n>>> ")
  
  ####
  # Removes references to nodes that do not exist
  ####
  def sanitize(self):
    retry = True
    while retry:
      retry = False
      for road in self.roadList:
        # for p in road.points:
        road.points = [p for p in road.points if p.node in self.nodeDict or p.node in self.mainMap.nodeDict]
        if len(road.points) == 0:
          self.roadList.remove(road)
          retry = True
          break

  ####
  # Imports all nodes and ways in a file and adds them to self.nodeDict and self.roadList
  #
  # filename is path of the OSM file
  ####
  def import_xml_file(self, filename):
    print("Importing file " + filename)
    tree = ET.parse(filename)
    root = tree.getroot()
    
    # Load all the nodes, using an extra components "tags"
    for node in root.iter('node'):
      this_node = CvtdNode(float(node.attrib['lat']), float(node.attrib['lon']))
      this_node.tags = {}
      this_node.attrib = node.attrib
      
      tag_keys = [t.attrib['k'] for t in node.iter('tag')]
      tag_vals = [t.attrib['v'] for t in node.iter('tag')]
      for ix, key in enumerate(tag_keys):
        this_node.tags[key] = tag_vals[ix]
      try:
        self.nodeDict[int(this_node.attrib['id'])] = this_node
      except KeyError:
        print("Fatal Error: Node did not have an ID field")
        return
    
    # Load all the ways, using an extra components "tags"
    for way in root.iter('way'):
      this_way = CvtdRoad()
      this_way.tags = {}
      this_way.attrib = way.attrib
      for nd in way.iter('nd'):
        p = CvtdRoadPoint(int(nd.attrib['ref']), None)
        this_way.points.append(p)
          
      tag_keys = [t.attrib['k'] for t in way.iter('tag')]
      tag_vals = [t.attrib['v'] for t in way.iter('tag')]
      for ix, key in enumerate(tag_keys):
        this_way.tags[key] = tag_vals[ix]
        if key == "name":
          this_way.name = tag_vals[ix]
      self.roadList.append(this_way)

  ####
  # Application entry point for importing an XML OSM file
  #
  # filename is path of the OSM file
  # mainMap is the CvtdMap that roads and nodes will be merged into
  ####
  def import_xml(self, filename, mainMap):
    self.mainMap = mainMap
    if os.path.isfile(filename):
      self.import_xml_file(filename)
    elif os.path.isdir(filename):
      for innerFilename in os.listdir(filename):
        filePath = filename + '/' + innerFilename
        if os.path.isfile(filePath) and innerFilename.endswith('.osm'):
          self.import_xml_file(filePath)
    else:
      print(f"Error: File {filename} does not exist.")
      return

    self.sanitize()

    # Give control to the user
    self.main()

  ####
  # Application entry point for importing OSM files
  #
  # filename is path of the OSM file
  # mainMap is the CvtdMap that roads and nodes will be merged into
  ####
  def begin_import(filename, mainMap):
    i = Importer()
    i.import_xml(filename, mainMap)

if __name__ == '__main__':
  try:
    filename = sys.argv[1]
    imp = Importer()
    imp.import_xml(filename, CvtdMap())
  except IndexError:
    print("Usage: python3 importer.py [OSM_filename]")