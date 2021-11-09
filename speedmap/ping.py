from datetime import datetime
from json import loads


class Ping:
    """
    Represents a single data ping describing time and location data for a bus relative to a stop_id

    Attributes:
        timestamp (int): time the data was recorded, in epoch time (milliseconds)
        stop_id (str): surrogate identifier of the related bus stop
        ping_type (str): a human readable operating mode of bus operation during the ping:
            values include 'DEPARTURE', 'MIDPATH', 'ARRIVAL'
        distance_from_stop (float): distance from the bus stop when the ping was recorded, in meters
    """

    def __init__(self, timestamp: datetime, stop_id: str, ping_type: str, distance_from_stop: float):
        self.timestamp = timestamp
        self.stop_id = stop_id
        self.ping_type = ping_type
        self.distance_from_stop = distance_from_stop

    @classmethod
    def from_json(cls, json_input_string: str):
        """
        Instantiates a new Ping class object from a json string representation

        Args:
            json_input_string (str): a json string representation of the Ping class

        Returns:
             a Ping class object

        Raises:
            KeyError: raised when input json is malformed or missing fields in Ping class object definition
        """

        # convert json string to dictionary
        input_dict = loads(json_input_string)

        # assign each key a value
        timestamp = input_dict["timestamp"]
        stop_id = input_dict["stopId"]
        ping_type = input_dict["pingType"]
        distance_from_stop = input_dict["distanceFromStop"]

        # instantiate ping object
        return Ping(timestamp, stop_id, ping_type, distance_from_stop)
