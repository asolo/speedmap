# Speedmap for Python3

The Speedmap module takes time and position data for a single bus traversing a 
single route and returns a speed map. The speed map is a collection of speed segments 
which describe the speed at any given point along the route in uniform distance increments. 

The module is executed from the command line with a file path and user input
"segment_length" which dictates the granularity or "mesh size" for the resulting speedmap.
Details for this execution are found below in this readme.

The module first creates a graph object from the ping data, 
inferring speed along the route between the actual data points. The module then applies the
segment "mesh" to this graph, using linear interpolation to determine the expected time
and position that the bus would be at each segment boundary. Once time and position are 
determined at the start and end of each segment, the average velocity for the segment is 
calculated based on the formula `v=dx/dt` where `dx` is the change in position, and `dt` 
is the change in time.

---
## Prerequisites

You will need to download and install python3.*. No external packages are required. 

## Executing speedmap module from the command line

Navigate to root directory `~/speedmap` and execute: 

```$ python3 -m speedmap <filepath> <segment_length>```

where `file_path` is a string containing the location of the input file and 
`segment_length` is a positive number containing the desired granularity of the speed map data

#### Example (to run with this repository)

The following command replicates the sample data input and output described in the problem statement.

```$ python3 -m speedmap data/mock_input.txt 50```

## Executing Unit Tests

Navigate to root directory `~/speedmap` and execute: 

```$ python3 -m unittest discover```

## Future areas of improvement and expansions

Future areas for improvement could include:

* Additional and more rigorous test cases
* Add a BusRoute class which can aggregate data for multiple BusOnRoute objects
* Add visualizations
