# cvtdapp
The CVTD application pulls the current bus data and displays the address on the console. This application
will also be able to pull locator history and guesstimate about future locations of the bus. The i
application opens roads.txt to access OSM data and uses the GTFS Importer to get GTFS data.

# roadtool
The Road Tool is used to search and add, edit and delete nodes, roads, cities and landmarks. It can also
use the GTFS Importer, which it can then use to generate a script to pull OSM data. The Road Tool's outputs
are roads.txt (also an input) and the Bash script to pull OSM data. Theoretically, the roadtool could also
launch the Importer to digest pulled OSM data.

# importer
The Importer imports an OSM file and turns it into roads.txt. It can also use the GTFS Importer to help
it know which roads in the OSM file are most useful.

# List of tasks
GTFS Importer finish importing everything
Design new route class and update everything
Importer choose most "interesting" roads to import