import sys
from speedmap.bus_on_route import BusOnRoute


def main():
    """
    Runs the speedmap module when executed from the command line interface and prints a collection of speed map segment
    objects as json to console

    Raises:
        FileNotFoundError: raised if input file path is not a valid input file
        ValueError: raised if segment_length cannot be parsed to a value
    """
    # validate arguments count
    if len(sys.argv)-1 != 2:
        raise SystemError("2 input arguments are expected, but " + str(len(sys.argv)-1) + " were given")

    # retrieve the command line arguments
    file_path = sys.argv[1]
    try:
        segment_length = float(sys.argv[2])
    except ValueError:
        raise ValueError("Segment length must be numeric")

    # instantiate a BusOnRoute object from file
    bus_on_route = BusOnRoute.from_file(file_path)

    # compute the speed map segments for the bus route
    segments = bus_on_route.get_speed_map(segment_length)

    # enumerate over each segment and print the output as a json
    for segment in segments:
        print(segment.__dict__)


if __name__ == "__main__":
    main()
