from typing import Iterable, Dict
from collections import namedtuple
from speedmap.ping import Ping
from speedmap.segment import Segment


class BusOnRoute:
    """
    Represents the data and methods describing a single bus on a single route

    Attributes:
        ping_list (Iterable(Ping): The list of data points sent from a bus indicating time, operation mode and
        relative position to bus stops
    """

    def __init__(self, ping_list: Iterable[Ping]):

        self.ping_list = ping_list

    @classmethod
    def from_file(cls, file_path: str):
        """
        Given an input file, reads and transforms each line into an array of Ping class objects that are sorted by time

        Args:
            file_path (str): the location of the raw input file containing a series of Pings

        Returns:
            a BusOnRoute class object
        """

        ping_list = []

        # open a read connection
        with open(file_path, "r") as file:
            for line in file:

                # deserialize each line into a Ping object
                ping = Ping.from_json(line)

                # append it to the ping array
                ping_list.append(ping)

        # sort the ping list by ascending timestamp so data is time-series
        ping_list.sort(key=lambda x: x.timestamp, reverse=False)

        # instantiate a new instance of the class
        return BusOnRoute(ping_list)

    def get_speed_map(self, segment_length: float) -> Iterable[Segment]:
        """
        Computes the speed at uniform user defined segment lengths based on ping data for a bus on a route

        Args:
            segment_length (float): a user defined length for a speed map segment, in meters

        Returns:
            Iterable[Segment]: an Iterable containing Segment class objects

        Raises:
            ValueError: if the segment length is invalid (less than 0)
            TypeError: if the segment length cannot be parsed to a value
        """

        # validate input
        if segment_length <= 0:
            raise ValueError("Segment length must be greater than 0")
        try:
            float(segment_length)
        except TypeError:
            raise TypeError("Segment length must be numeric")

        # compute total lengths of each stop
        stop_lengths = self._get_stop_lengths()

        # compute the speed graph, or the speed between each pair of data pings
        speed_graph = self._get_speed_graph()

        # initialize results set
        speed_map_segments = []

        # iterate over each stop_id
        for stop_id in stop_lengths.keys():

            # initialize target data for while loop and indexes
            segment_time_start, segment_time_end = None, None
            speed_graph_of_stop_index, segment_index = 0, 0
            stop_length = stop_lengths[stop_id]
            speed_graph_for_stop = speed_graph[stop_id]

            # iterate over segments within a stop_id
            while segment_index * segment_length < stop_length:

                # get the next edge on the speed graph
                speed_graph_edge = speed_graph_for_stop[speed_graph_of_stop_index]

                # determine the start and end distances of the current segment
                segment_distance_start = segment_index * segment_length
                segment_distance_end = segment_distance_start + segment_length if\
                    segment_distance_start + segment_length <= stop_length else stop_length

                # figure out if the current segment start is before the end of the current speed graph edge
                if speed_graph_edge.distance_end > segment_distance_start and segment_time_start is None:

                    # linearly interpolate the time at the start of the segment using
                    # dx/dt = (d2-d1)/(t2-t1) = v, rearranged to find t1: t1 = t2 - (d2 - d1)/v
                    # and include conversion from milliseconds to seconds
                    segment_time_start = speed_graph_edge.time_end / 1000 \
                        - (speed_graph_edge.distance_end - segment_distance_start) / speed_graph_edge.speed

                # figure out if the current segment end is at or before the end of the current speed graph edge.
                if speed_graph_edge.distance_end >= segment_distance_end and segment_time_end is None:

                    # linearly interpolate the time at the end of the segment
                    segment_time_end = speed_graph_edge.time_end / 1000 \
                        - (speed_graph_edge.distance_end - segment_distance_end) / speed_graph_edge.speed

                # check if we have both segment start and end times computed
                if segment_time_start is not None and segment_time_end is not None:
                    
                    # great! now we can use dx/dt = v to calculate the speed of this segment 
                    speed = (segment_distance_end - segment_distance_start) / (segment_time_end - segment_time_start)

                    # format the speed result to 1 decimal place
                    speed = float('%.1f' % round(speed, 1))

                    # convert result to a speed map segment object
                    speed_map_segment = Segment(
                        stop_id=stop_id,
                        segment_index=segment_index,
                        segment_length=segment_distance_end - segment_distance_start,
                        speed=speed)

                    # add to results set
                    speed_map_segments.append(speed_map_segment)

                    # reinitialize the segment times, increment the segment index
                    segment_time_start, segment_time_end = None, None
                    segment_index += 1
                else:
                    # if we haven't found both segment start and end times, increment to the next speed graph edge
                    speed_graph_of_stop_index += 1

        return speed_map_segments

    def _get_stop_lengths(self) -> Dict[str, float]:
        """
        Gets a dictionary containing the total distance between each stop

        Returns:
            Dict[str, float]: A dictionary where keys are stop_id and values are the total distance to the next stop_id,
                in meters
        """

        stop_id_lengths = {}

        for ping in self.ping_list:
            if ping.ping_type == 'ARRIVAL' and ping.stop_id not in stop_id_lengths:
                stop_id_lengths[ping.stop_id] = ping.distance_from_stop

        return stop_id_lengths

    def _get_speed_graph(self) -> Dict[str, Iterable[namedtuple]]:
        """
        Gets a speed graph representation of bus route data, where speed is calculated between each sequential ping

        Returns:
            Dict[str, Iterable[namedtuple]: A dictionary where the keys are stop_id, and the values are arrays of
                speed graph edges for the relevant stop_id key
        """
        speed_graph = {}
        pings_count = len(self.ping_list)

        # loop over ping data
        for i in range(0, pings_count-1):

            # observe the current ping and the next ping in the series
            ping = self.ping_list[i]
            next_ping = self.ping_list[i+1]

            # add the stop_id to the dictionary keys if not already there
            if ping.stop_id not in speed_graph:
                speed_graph[ping.stop_id] = []

            # ignore any pair of pings where the first ping is an 'ARRIVAL' type
            if ping.ping_type in ('DEPARTURE', 'MIDPATH'):

                # compute velocity where v = dx/dt = (distance traveled/time elapsed) and
                # convert from meters/millisecond to meters/second
                speed = (next_ping.distance_from_stop - ping.distance_from_stop) / (
                            next_ping.timestamp - ping.timestamp) * 1000

                # define a speed graph edge, which defines speed, time, and distance between each data ping pair
                SpeedGraphEdge = namedtuple('SpeedGraphEdge', ['stop_id', 'speed', 'distance_end', 'time_end'])
                speed_graph_edge = SpeedGraphEdge(
                    stop_id=ping.stop_id,
                    speed=speed,
                    distance_end=next_ping.distance_from_stop,
                    time_end=next_ping.timestamp
                )

                # add edge to speed graph, grouping data by stop_ids
                speed_graph[ping.stop_id].append(speed_graph_edge)

        return speed_graph
