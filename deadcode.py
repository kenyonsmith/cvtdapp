#### This file contains code that I don't need but don't have the heart to delete yet
# This includes the following:
# Route creation code for before I switched to GTFS routes

####
# new_route directs the user to create a new route and guides them through the process
####
def new_route(map):
  this_route = CvtdRoute()
  define_route_segments(this_route)
  if not GOOGLE_DIRECTORY or input(f'Use the following Google directory: ({GOOGLE_DIRECTORY})? (y/n) ') != 'y':
    goodPath = False
    keepTrying = True
    while not goodPath and keepTrying:
      GOOGLE_DIRECTORY = input('Enter the directory for the Google Transit files: ')
      if not os.path.isdir(GOOGLE_DIRECTORY):
        keepTrying = input(f'Error: The directory {GOOGLE_DIRECTORY} does not exist. Try again? (y/n) ') == 'y'

####
# define_route_segments directs the user to create a new route and guides them through the process
####
def define_route_segments(this_route):
  # Let them choose a starting point, like Wilder Rd, then list the names of the roads and the terminuses.
  # Let them choose one and an address.
  # Then let them choose an intersecting road to turn on, or return to the starting position

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
