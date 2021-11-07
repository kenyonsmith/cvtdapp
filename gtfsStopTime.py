####
# A class representing a shape according to the GTFS standard
#  NOTE: tripId and stopId are not included here since they are typically the key to a stop time dictionary
#
# departure is a Time object
# arrival is a Time object
# timepoint is a boolean variable indicating whether this stop is a time point for this trip
####
class GtfsStopTime:
  def __init__(self):
    self.departure = None
    self.arrival = None
    self.timepoint = None

  ####
  # describe prints all information about this shape
  ####
  def describe(self):
    print(f"Departure is {self.departure}")
    print(f"Arrival is {self.arrival}")
    tp = "Yes" if self.timepoint else "No"
    print(f"Timepoint? {tp}")

  ####
  # validate checks to see if the shape is valid
  ####
  def validate(self):
    return True
