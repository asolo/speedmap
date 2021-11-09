import unittest
import os
from pathlib import Path
import sys

sys.path.append(os.path.join(os.path.abspath(os.path.curdir), '..'))
from speedmap.bus_on_route import BusOnRoute
from speedmap.segment import Segment


class TestBusRoute(unittest.TestCase):

    def test_from_file_when_no_file_throws(self):

        # Arrange
        mock_data_dir = Path(os.path.dirname(__file__))  # relative directory path

        test_file_path = mock_data_dir / "bogus_mock_input.txt"

        # Act & Assert
        with self.assertRaises(FileNotFoundError):
            BusOnRoute.from_file(test_file_path)

    def test_from_file_when_valid_file_succeeds(self):

        # Arrange
        mock_data_dir = Path(os.path.dirname(__file__))  # relative directory path

        test_file_path = mock_data_dir / "../data/mock_input.txt"

        # Act
        test_object = BusOnRoute.from_file(test_file_path)

        # Assert
        self.assertIsNotNone(test_object)
        self.assertEqual(5, len(test_object.ping_list))
        self.assertEqual(10000, test_object.ping_list[0].timestamp)
        self.assertEqual('1234', test_object.ping_list[0].stop_id)
        self.assertEqual('DEPARTURE', test_object.ping_list[0].ping_type)
        self.assertEqual(0.0, test_object.ping_list[0].distance_from_stop)

    def test_get_stop_id_lengths(self):

        # Arrange
        mock_data_dir = Path(os.path.dirname(__file__))  # relative directory path
        test_file_path = mock_data_dir / "../data/mock_input.txt"
        target = BusOnRoute.from_file(test_file_path)

        # Act
        result = target._get_stop_lengths()

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(2, len(result))
        self.assertEqual(75, result['1234'])
        self.assertEqual(100, result['5678'])

    def test_get_stop_id_lengths_with_single_stop(self):
        # Arrange
        mock_data_dir = Path(os.path.dirname(__file__))  # relative directory path
        test_file_path = mock_data_dir / "../data/mock_input2.txt"
        target = BusOnRoute.from_file(test_file_path)

        # Act
        result = target._get_stop_lengths()

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(1, len(result))
        self.assertEqual(80, result['1'])

    def test_get_speed_graph(self):
        # Arrange
        mock_data_dir = Path(os.path.dirname(__file__))  # relative directory path
        test_file_path = mock_data_dir / "../data/mock_input.txt"
        target = BusOnRoute.from_file(test_file_path)

        # Act
        result = target._get_speed_graph()

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(2, len(result))
        self.assertEqual(1, len(result['1234']))
        self.assertEqual(2, len(result['5678']))

        # assert the first graph edge of stopid '1234'
        self.assert_speed_graph_edges_equal(
            actual_graph_edge=result['1234'][0],
            expected_speed=3.0,
            expected_stop_id='1234',
            expected_distance_end=75.0,
            expected_time_end=35000
        )

        # assert the first graph edge of stopid '5678'
        self.assert_speed_graph_edges_equal(
            actual_graph_edge=result['5678'][0],
            expected_speed=3.0,
            expected_stop_id='5678',
            expected_distance_end=75.0,
            expected_time_end=65000
        )

        # assert the second graph edge of stopid '5678'
        self.assert_speed_graph_edges_equal(
            actual_graph_edge=result['5678'][1],
            expected_speed=1.0,
            expected_stop_id='5678',
            expected_distance_end=100.0,
            expected_time_end=90000
        )

    def test_get_speed_graph_with_zero_and_reverse(self):
        # Arrange
        mock_data_dir = Path(os.path.dirname(__file__))  # relative directory path
        test_file_path = mock_data_dir / "../data/mock_input2.txt"
        target = BusOnRoute.from_file(test_file_path)

        # Act
        result = target._get_speed_graph()

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(1, len(result))
        self.assertEqual(9, len(result['1']))

        # assert the first graph edge of stopid '1'
        self.assert_speed_graph_edges_equal(
            actual_graph_edge=result['1'][0],
            expected_speed=11.0,
            expected_stop_id='1',
            expected_distance_end=11.0,
            expected_time_end=11000
        )

        # assert the graph edge of stopid '1' where speed is 0
        self.assert_speed_graph_edges_equal(
            actual_graph_edge=result['1'][1],
            expected_speed=0.0,
            expected_stop_id='1',
            expected_distance_end=11.0,
            expected_time_end=12000
        )

        # assert the graph edge of stopid '1' where speed is negative
        self.assert_speed_graph_edges_equal(
            actual_graph_edge=result['1'][6],
            expected_speed=-1.0,
            expected_stop_id='1',
            expected_distance_end=59.0,
            expected_time_end=17000
        )

    def test_get_speed_segments_example_case(self):
        # Arrange
        mock_data_dir = Path(os.path.dirname(__file__))  # relative directory path

        test_file_path = mock_data_dir / "../data/mock_input.txt"

        expected_segment_1 = Segment('1234', 0, 50.0, 3.0)
        expected_segment_2 = Segment('1234', 1, 25.0, 3.0)
        expected_segment_3 = Segment('5678', 0, 50.0, 3.0)
        expected_segment_4 = Segment('5678', 1, 50.0, 1.5)

        target = BusOnRoute.from_file(test_file_path)

        # Act
        result = target.get_speed_map(
            segment_length=50)

        # Assert
        self.assertEqual(4, len(result))
        self.assert_segments_equal(expected_segment_1, result[0])
        self.assert_segments_equal(expected_segment_2, result[1])
        self.assert_segments_equal(expected_segment_3, result[2])
        self.assert_segments_equal(expected_segment_4, result[3])

    def test_get_speed_segments_when_segment_large(self):
        # Arrange
        mock_data_dir = Path(os.path.dirname(__file__))  # relative directory path

        test_file_path = mock_data_dir / "../data/mock_input.txt"

        expected_segment_1 = Segment('1234', 0, 75.0, 3.0)
        expected_segment_2 = Segment('5678', 0, 100.0, 2.0)

        target = BusOnRoute.from_file(test_file_path)

        # test all segments in first stop id
        result = target.get_speed_map(
            segment_length=1000)

        self.assertEqual(2, len(result))
        self.assert_segments_equal(expected_segment_1, result[0])
        self.assert_segments_equal(expected_segment_2, result[1])

    def test_get_speed_segments_when_segment_small(self):
        # Arrange
        mock_data_dir = Path(os.path.dirname(__file__))  # relative directory path

        test_file_path = mock_data_dir / "../data/mock_input.txt"

        # first segment
        expected_segment_1 = Segment(stop_id='1234', segment_index=0, segment_length=1.0, speed=3.0)

        # before and after step change in speed
        expected_segment_2 = Segment(stop_id='5678', segment_index=74, segment_length=1.0, speed=3.0)
        expected_segment_3 = Segment(stop_id='5678', segment_index=75, segment_length=1.0, speed=1.0)

        # last segment
        expected_segment_4 = Segment(stop_id='5678', segment_index=99, segment_length=1.0, speed=1.0)

        target = BusOnRoute.from_file(test_file_path)

        # test all segments in first stop id
        result = target.get_speed_map(
            segment_length=1)

        self.assertEqual(175, len(result))
        self.assert_segments_equal(expected_segment_1, result[0])
        self.assert_segments_equal(expected_segment_2, result[149])
        self.assert_segments_equal(expected_segment_3, result[150])
        self.assert_segments_equal(expected_segment_4, result[174])

    def test_get_speed_segments_for_case_2(self):
        # Arrange
        mock_data_dir = Path(os.path.dirname(__file__))  # relative directory path

        test_file_path = mock_data_dir / "../data/mock_input2.txt"

        # first segment
        expected_segment_1 = Segment(stop_id='1', segment_index=0, segment_length=10.0, speed=11.0)

        # during high speed segment and after step change in speed
        expected_segment_2 = Segment(stop_id='1', segment_index=4, segment_length=10.0, speed=39.0)

        # during direction change
        expected_segment_3 = Segment(stop_id='1', segment_index=5, segment_length=10.0, speed=3.3)

        # last segment
        expected_segment_4 = Segment(stop_id='1', segment_index=7, segment_length=10.0, speed=10.0)

        target = BusOnRoute.from_file(test_file_path)

        # test all segments in first stop id
        result = target.get_speed_map(
            segment_length=10)

        self.assertEqual(8, len(result))
        self.assert_segments_equal(expected_segment_1, result[0])
        self.assert_segments_equal(expected_segment_2, result[4])
        self.assert_segments_equal(expected_segment_3, result[5])
        self.assert_segments_equal(expected_segment_4, result[7])

    def test_get_speed_segments_for_case_2_when_one_segment(self):
        # Arrange
        mock_data_dir = Path(os.path.dirname(__file__))  # relative directory path

        test_file_path = mock_data_dir / "../data/mock_input2.txt"

        # first segment
        expected_segment_1 = Segment(stop_id='1', segment_index=0, segment_length=80.0, speed=8.9)

        target = BusOnRoute.from_file(test_file_path)

        # test all segments in first stop id
        result = target.get_speed_map(
            segment_length=1000)

        self.assertEqual(1, len(result))
        self.assert_segments_equal(expected_segment_1, result[0])

    def test_get_speed_segments_when_segment_invalid(self):
        # Arrange
        mock_data_dir = Path(os.path.dirname(__file__))  # relative directory path

        test_file_path = mock_data_dir / "../data/mock_input.txt"
        target = BusOnRoute.from_file(test_file_path)

        # Act & Assert
        with self.assertRaises(ValueError):
            result = target.get_speed_map(
                segment_length=0)

    def test_get_speed_segments_when_segment_is_non_numeric(self):
        # Arrange
        mock_data_dir = Path(os.path.dirname(__file__))  # relative directory path

        test_file_path = mock_data_dir / "../data/mock_input.txt"
        target = BusOnRoute.from_file(test_file_path)

        # Act & Assert
        with self.assertRaises(TypeError):
            result = target.get_speed_map(
                segment_length='a')

    def assert_segments_equal(self, expected_segment: Segment, actual_segment: Segment) -> bool:
        self.assertEqual(expected_segment.stop_id, actual_segment.stop_id)
        self.assertAlmostEqual(expected_segment.segment_length, actual_segment.segment_length)
        self.assertEqual(expected_segment.segment_index, actual_segment.segment_index)
        self.assertAlmostEqual(expected_segment.speed, actual_segment.speed)

    def assert_speed_graph_edges_equal(
            self,
            actual_graph_edge,
            expected_stop_id,
            expected_speed,
            expected_distance_end,
            expected_time_end) -> bool:

        self.assertEqual(expected_distance_end, actual_graph_edge.distance_end)
        self.assertEqual(expected_stop_id, actual_graph_edge.stop_id)
        self.assertAlmostEqual(expected_speed, actual_graph_edge.speed)
        self.assertEqual(expected_time_end, actual_graph_edge.time_end)


if __name__ == '__main__':
    unittest.main()