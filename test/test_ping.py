import unittest
import os
import sys
sys.path.append(os.path.join(os.path.abspath(os.path.curdir), '..'))
from speedmap.ping import Ping


class TestPing(unittest.TestCase):

    def test_from_json_when_valid_object_succeeds(self):

        # Arrange
        test_json = '{"timestamp": 10000, "stopId": "1234", "pingType": "DEPARTURE", "distanceFromStop": 0.0}'

        # Act
        test_object = Ping.from_json(test_json)

        # Assert that each field deserializes correctly
        self.assertEqual(test_object.timestamp, 10000)
        self.assertEqual(test_object.stop_id, "1234")
        self.assertEqual(test_object.ping_type, "DEPARTURE")
        self.assertEqual(test_object.distance_from_stop, 0.0)

    def test_from_json_when_invalid_object_throws(self):
        # Arrange
        test_json = '{"timestamp": 10000, "foo": "1234", "pingType": "DEPARTURE", "distanceFromStop": 0.0}'

        # Act & Assert:
        with self.assertRaises(KeyError):
            Ping.from_json(test_json)


if __name__ == '__main__':
    unittest.main()
