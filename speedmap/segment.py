class Segment:
    """
    Represents a segment of the speed map output.

    Attributes:
        stop_id (str): surrogate identifier of the related bus stop
        segment_index (int): the relative order of a segment within all segments for a stop_id
        segment_length (float): the length of the segment, in meters
        speed (float): the speed of the bus during travel on this segment, in meters/second
    """

    def __init__(self, stop_id: str, segment_index: int, segment_length: float, speed: float):

        self.stop_id = stop_id
        self.segment_index = segment_index
        self.segment_length = segment_length
        self.speed = speed
