import numpy as np
from datetime import datetime

# CRD file parser

# Header lines H1 to H9 define one "unit"
# Header lines H4 to H8 define one session

# station metadata from H2
# target metadata from H3
# Config metadata C0, C1, C2, C3, C4
# All of these metadata can be either in session or unit.
# Have to ask session for metadata, and if not available, delegate request to unit.
# TODO: Load metadata in order, warn if session defines metadata already in unit.

# Inside session, time series data comes from record types 10, 11, and 12 (ranges), 
# 20 and 21 (meteo), 30 (angles) and 40 (calibration).
# Also type 50 (pass statistics) can appear.
# The time series stuff should go in a Pandas dataframe?



def parse_unit(line):
    """Parse a H1 line into a unit dict."""
    if not line.startswith("H1"):
        raise ValueError("Not H1 line for unit parser!")
    timestamp = {
        "year" : int(line[10:14]),
        "month" : int(line[15:17]),
        "day" : int(line[18:20]),
        "hour" : int(line[21:23])
    }
    return {
        "format" : line[3:6],
        "version" : line[7:9].strip(),
        "time" : datetime(**timestamp),
        "sessions" : []
    }

def parse_session(line):
    """Parse H4 line into session."""
    if not line.startswith("H4"):
        raise ValueError("Not H4 line for session parser!")
    return {
        "data" : None,
        "start" : datetime(
            year = int(line[6:10]),
            month = int(line[11:13]),
            day = int(line[14:16]),
            hour = int(line[17:19]),
            minute = int(line[20:22]),
            second = int(line[23:25])
        ),
        "end" : datetime(
            year = int(line[26:30]),
            month = int(line[31:33]),
            day = int(line[34:36]),
            hour = int(line[37:39]),
            minute = int(line[40:42]),
            second = int(line[43:45])
        ),
        "troposphere_corrected" :  int(line[49]),
        "CoM_corrected" : int(line[51]),
        "receive_amplitude_corrected" : int(line[53]),
        "station_delay_corrected" : int(line[55]),
        "spacecraft_delay_corrected" : int(line[57]),
        "range_type" : int(line[59]),
        "data_quality" : int(line[61])
    }


def parse_station(line):
    if not line.startswith("H2"):
        raise ValueError("Not H2 line for Station constructor!")
    return {
        "name" : line[3:13].strip(),
        "ID" : int(line[14:18]),
        "system" : int(line[19:21]),
        "occupancy" : int(line[22:24]),
        "timescale" : int(line[25:27])
    }


def parse_target(line):
    """Parse H3 line for target parameters."""
    if not line.startswith("H3"):
        raise ValueError("Not H3 line for Target constructor!")
    return {
        "name" : line[3:13].strip(),
        "ID" : int(line[14:22]),
        "SIC" : int(line[23:27]),
        "NORAD" : int(line[28:36]),
        "timescale" : int(line[37:38]),
        "type" : int(line[39])
    }

def parse_CRD(data):
    active_unit = None
    active_session = None
    active_data = []
    units = []
    for line in data.split("\n"):
        line = line.upper()
        if line.startswith("H1"):
            # Start of unit.
            active_unit = parse_unit(line)
            units.append(active_unit)
        if line.startswith("H9"):
            # End of unit.
            active_unit = None
        if line.startswith("H4"):
            # Start of session, add new session to active unit.
            active_session = parse_session(line)
            active_unit["sessions"].append(active_session)
        if line.startswith("H8"):
            # End of session, convert active_data into array and save to
            # active session.
            active_session["data"] = np.array(active_data)
            active_data = []
            active_session = None
        if line.startswith("H2"):
            # Station definition, add station to active session, 
            # or to active unit if no active session.
            if active_session is None:
                active_unit["station"] = parse_station(line)
            else:
                active_session["station"] = parse_station(line)
        if line.startswith("H3"):
            # Target definition, add new target to active session, 
            # or to active unit if no active session.
            if active_session is None:
                active_unit["target"] = parse_target(line)
            else:
                active_session["target"] = parse_target(line)
        if line.startswith("10"):
            # Data point, add to active_data.
            sline = line.split()
            t = float(sline[1])
            r = float(sline[2])
            active_data.append([t, r])
    return units
        




if __name__=="__main__":
    from sys import argv
    import json
    with open(argv[1]) as f:
        Units = parse_CRD(f.read())
        print(json.dumps(Units[0], default=str, indent=4))

