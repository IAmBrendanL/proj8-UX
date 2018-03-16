"""
Open and close time calculations
for ACP-sanctioned brevets
following rules described at https://rusa.org/octime_alg.html
and https://rusa.org/pages/rulesForRiders
"""
import arrow
import math

#  Note for CIS 322 Fall 2016:
#  You MUST provide the following two functions
#  with these signatures, so that I can write
#  automated tests for grading.  You must keep
#  these signatures even if you don't use all the
#  same arguments.  Arguments are explained in the
#  javadoc comments.
#


def open_time(control_dist_km, brevet_dist_km, brevet_start_time):
    """
    Args:
       control_dist_km:  number, the control distance in kilometers
       brevet_dist_km: number, the nominal distance of the brevet
           in kilometers, which must be one of 200, 300, 400, 600,
           or 1000 (the only official ACP brevet distances)
       brevet_start_time:  An ISO 8601 format date-time string indicating
           the official start time of the brevet
    Returns:
       An ISO 8601 format date string indicating the control open time.
       This will be in the same time zone as the brevet start time.
    """
    speed = [(600, 28), (400, 30), (200, 32), (0, 34)]
    time_diff = 0
    # calculate time diff in hours
    for item in speed:
        if control_dist_km > item[0]:
            time_diff += (control_dist_km - item[0]) / item[1]
            control_dist_km -= control_dist_km - item[0]

    # shift time arrow by time_diff
    open_arrow = arrow.get(brevet_start_time)
    open_arrow = open_arrow.shift(hours=+time_diff // 1,
                                  minutes=+round((time_diff % 1)*60))
    return open_arrow.isoformat()




def close_time(control_dist_km, brevet_dist_km, brevet_start_time):
    """
    Args:
       control_dist_km:  number, the control distance in kilometers
          brevet_dist_km: number, the nominal distance of the brevet
          in kilometers, which must be one of 200, 300, 400, 600, or 1000
          (the only official ACP brevet distances)
       brevet_start_time:  An ISO 8601 format date-time string indicating
           the official start time of the brevet
    Returns:
       An ISO 8601 format date string indicating the control close time.
       This will be in the same time zone as the brevet start time.
    """
    speed = [(600, 11.428), (400, 15), (200, 15), (0, 15)]
    # holds constant end value distances for different length races
    end_times_dict = {0: 1, 200: 13.5, 300: 20, 400: 27, 600: 40, 1000: 75}

    # check if control_dist_km is length of race or 0 and compute constant end time
    if control_dist_km == brevet_dist_km or control_dist_km == 0:
        time_diff = end_times_dict[control_dist_km]
        close_arrow = arrow.get(brevet_start_time)
        # compute shift and round down
        close_arrow = close_arrow.shift(hours=+time_diff // 1,
                                        minutes=+round((time_diff % 1)*60))
        return close_arrow.isoformat()

    # else, calculate time diff in hours
    time_diff = 0
    for item in speed:
        if control_dist_km > item[0]:
            time_diff += (control_dist_km - item[0]) / item[1]
            control_dist_km -= control_dist_km - item[0]

    # shift time arrow by time_diff
    close_arrow = arrow.get(brevet_start_time)
    close_arrow = close_arrow.shift(hours=+time_diff // 1,
                                    minutes=+round((time_diff % 1)*60))
    return close_arrow.isoformat()



