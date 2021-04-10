import xml.etree.ElementTree as ET

from cvtdNode import CvtdNode
from cvtdRoad import CvtdRoad
from cvtdRoadPoint import CvtdRoadPoint
from cvtdMap import CvtdMap
from cvtdUtil import CvtdUtil

####
# Imports an XML file 
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
    print("\n(1) Search for a road with the following name")
  
  ####
  # Merges roads in a Road List based on beginning/ending node
  #
  # roadList is the list of roads to merge
  ####
  # def merge_ways(self, roadList):
  #   mergeFound = True
  #   lastWix = 0
  #   while mergeFound:
  #     mergeFound = False
  #     for wix, way in enumerate(roadList[lastWix:]):
  #       for cmpix, cmpway in enumerate(roadList):
  #         if way is not cmpway:
  #           if way.points[0].node == cmpway.points[0].node and way.name == cmpway.name:
  #             way.points = list(reversed(cmpway.points[1:])) + way.points
  #             mergeFound = True
  #           elif way.points[0].node == cmpway.points[-1].node and way.name == cmpway.name:
  #             way.points = cmpway.points[:-1] + way.points
  #             mergeFound = True
  #           elif way.points[-1].node == cmpway.points[0].node and way.name == cmpway.name:
  #             way.points = way.points + cmpway.points[1:]
  #             mergeFound = True
  #           elif way.points[-1].node == cmpway.points[-1].node and way.name == cmpway.name:
  #             way.points = way.points + list(reversed(cmpway.points[:-1]))
  #             mergeFound = True
  #         if mergeFound:
  #           print(f"Merged two instances of {way.name}, list length is {len(roadList)}")
  #           del roadList[cmpix]
  #           break
  #       if mergeFound:
  #         break
  #       else:
  #         lastWix = wix
  
  ####
  # search_road searches for roads that match the given name, and helps the user to merge them in the main map
  ####
  def search_road(self):
    search = input("Search for a road with the following text: ")
    ways = [way for way in self.roadList if search in way.name]

    if len(ways) == 0:
      print("No ways found.")
      return

    # Print information about each of the matching ways
    for ix, way in enumerate(ways):
      print(f"[{ix+1}]: {way.name} has {len(way.points)} nodes")
      print(" " + ", ".join([f"({self.nodeDict[p.node].lat}, {self.nodeDict[p.node].lon})" for p in way.points]))
    
    # Here, compare with what is currently in the file to see if we want to add onto a road, modify a road, or do nothing
    # For the present, we'll just add a new road
    newRoad = CvtdRoad()
    newNodes = []
    nodeOffset = len(self.mainMap.nodeList)

    whichWay = CvtdUtil.input_int("Adding a new road. Start with which way? ", 1, len(ways)) - 1
    if whichWay:
      newRoad.name = ways[whichWay].name
      newRoad.dir = input(f"Enter a direction for {newRoad.name} ('N/S', 'E/W', or other'): ")
      minValue = None
      maxValue = None
      lastValue = None

      # For each point in this way
      pointList = ways[whichWay].points
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
          addr = CvtdUtil.input_int("Enter the address for this point, or 'skip' or 'return': ", minValue, maxValue, neValue, ['skip', 'return', 's', 'r'])
          if addr is not None:
            if addr in ["skip", 's']:
              pass
            elif addr in ["return", 'r']:
              returnPointList.append(point)
            else:
              newRoad.points.append(CvtdRoadPoint(point.node, addr))
          else:
            return
        
        pointList = returnPointList
      
      # They successfully added all the points

      # Here, you should find out if they want to combine this way with any other ways
      print("\nYou've defined the following road:")
      newRoad.describe(self.nodeDict)
      confirm = input("Add this new road to your map? (y/n): ") == 'y'
      if confirm:
        self.mainMap.add_street_with_nodes(newRoad, self.nodeDict)

  ####
  # main function as seen by the user
  ####
  def main(self):
    command = "help"
    while command not in ["quit", "exit", "q", "e"]:
      if command == "1":
        self.search_road()
      else:
        self.show_help()
      command = input("\n>>> ")

  ####
  # Application entry point for importing an XML OSM file
  #
  # filename is path of the OSM file
  # mainMap is the CvtdMap that roads and nodes will be merged into
  ####
  def import_xml(self, filename, mainMap):
    tree = ET.parse(filename)
    root = tree.getroot()

    self.mainMap = mainMap

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

    # Give control to the user
    self.main()

if __name__ == '__main__':
    imp = Importer()
    # imp.import_xml('/mnt/c/Users/ksmith/Downloads/map.osm', CvtdMap())
    imp.import_xml('/mnt/c/Users/ksmith/Documents/Notes/CVTD/map.osm', CvtdMap())