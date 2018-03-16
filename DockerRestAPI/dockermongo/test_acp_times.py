"""
Author: Brendan Lindsey

Nose tests for acp_times.py
"""
import nose
import acp_times
import arrow

def test_zero():
    """
    Start must open when race starts and end 1 hr afterwards
    """
    test_open = acp_times.open_time(0, 200, "2017-01-01T00:00:00-08:00") == "2017-01-01T00:00:00-08:00"
    test_close = acp_times.close_time(0, 200, "2017-01-01T00:00:00-08:00") == "2017-01-01T01:00:00-08:00"
    assert test_open and test_close


def test_splits():
    """
    Verify that data is correctly split on speed changes
    """
    speeds = [(0, "2017-01-01T00:00:00-08:00", "2017-01-01T01:00:00-08:00"),
              (200, "2017-01-01T05:53:00-08:00", "2017-01-01T13:20:00-08:00"),
              (400, "2017-01-01T12:08:00-08:00", "2017-01-02T02:40:00-08:00"),
              (600, "2017-01-01T18:48:00-08:00", "2017-01-02T16:00:00-08:00"),
              (1000, "2017-01-02T09:05:00-08:00", "2017-01-04T03:00:00-08:00")]

    result = True
    for item in speeds:
        test_open = acp_times.open_time(item[0], 1000, "2017-01-01T00:00:00-08:00") == item[1]
        test_close = acp_times.close_time(item[0], 1000, "2017-01-01T00:00:00-08:00") == item[2]
        result = test_open and test_close and result

    assert result


def test_middle_value():
    """
    Tests values in the middle of splits
    """
    speeds = [(150, "2017-01-01T04:25:00-08:00", "2017-01-01T10:00:00-08:00"),
              (841, "2017-01-02T03:24:00-08:00", "2017-01-03T13:05:00-08:00"),
              (531, "2017-01-01T16:30:00-08:00", "2017-01-02T11:24:00-08:00")]

    result = True
    for item in speeds:
        test_open = acp_times.open_time(item[0], 1000, "2017-01-01T00:00:00-08:00") == item[1]
        test_close = acp_times.close_time(item[0], 1000, "2017-01-01T00:00:00-08:00") == item[2]
        result = test_open and test_close and result

    assert result


def test_200_end():
    """
    Tests for the end time case of 200km brevets having to be 10 min longer per spec
    """
    assert acp_times.close_time(200, 200, "2017-01-01T00:00:00-08:00") == "2017-01-01T13:30:00-08:00"


def test_datetime():
    """
    Verify that different datetimes return the same difference in time
    """
    a = arrow.now()
    b = a.shift(days=-3.33)

    result = True
    for item in a, b:
        test_open = acp_times.open_time(200, 200, item) == item.shift(hours=+5, minutes=+53).isoformat()
        test_close = acp_times.close_time(200, 200, item) == item.shift(hours=+13.5).isoformat()
        result = test_open and test_close and result

    assert result
