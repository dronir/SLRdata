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


class Unit:
    def __init__(self, line):
        if not line.startswith("H1"):
            raise ValueError("Not H1 line for Unit constructor!")
        self.line = line
        self.format = line[3:6]
        self.version = line[7:9]
        Y = line[10:14]
        M = line[15:17]
        D = line[18:20]
        h = line[21:23]
        self.time = "{}-{}-{} {}h".format(Y,M,D,h)
        self.sessions = []
    def __repr__(self):
        return "Unit('{}') with {} sessions".format(self.line, len(self.sessions))
        
    @property
    def station(self):
        return self._station
    @station.setter
    def station(self, value):
        self._station = value
    @station.deleter
    def station(self):
        del self._station
    
    @property
    def target(self):
        return self._target
    @target.setter
    def target(self, value):
        self._target = value
    @target.deleter
    def target(self):
        del self._target

class Session:
    def __init__(self, line):
        if not line.startswith("H4"):
            raise ValueError("Not H4 line for Session constructor!")
        self.line = line
        self.data = None
        self.start = datetime(
            year = int(line[6:10]),
            month = int(line[11:13]),
            day = int(line[14:16]),
            hour = int(line[17:19]),
            minute = int(line[20:22]),
            second = int(line[23:25])
        )
        self.end = datetime(
            year = int(line[26:30]),
            month = int(line[31:33]),
            day = int(line[34:36]),
            hour = int(line[37:39]),
            minute = int(line[40:42]),
            second = int(line[43:45])
        )

    @property
    def station(self):
        if hasattr(self, "_station"):
            return self._station
        else:
            return self.unit.station
    @station.setter
    def station(self, value):
        self._station = value
    @station.deleter
    def station(self):
        del self._station
    
    @property
    def target(self):
        if hasattr(self, "_target"):
            return self._target
        else:
            return self.unit.target
    @target.setter
    def target(self, value):
        self._target = value
    @target.deleter
    def target(self):
        del self._target
    
    def __repr__(self):
        return "Session({}) [Session with {} data points]".format(self.line, self.data.shape[0])


class Station:
    def __init__(self, line):
        if not line.startswith("H2"):
            raise ValueError("Not H2 line for Station constructor!")
        self.line = line
        self.name = line[3:13].strip()
        self.ID = int(line[14:18])
        self.system = int(line[19:21])
        self.occupancy = int(line[22:24])
        self.timescale = int(line[25:27])
    def __repr__(self):
        return "Station('{}')".format(self.line)

class Target:
    def __init__(self, line):
        if not line.startswith("H3"):
            raise ValueError("Not H3 line for Target constructor!")
        self.line = line
        self.name = line[3:13].strip()
        self.ID = int(line[14:22])
        self.SIC = int(line[23:27])
        self.NORAD = int(line[28:36])
        self.timescale = int(line[37:38])
        self.type = int(line[39])
    def __repr__(self):
        return "Target('{}')".format(self.line)



def parse_CRD(data):
    active_unit = None
    active_session = None
    active_data = []
    units = []
    for line in data.split("\n"):
        line = line.upper()
        if line.startswith("H1"):
            # Start of unit
            active_unit = Unit(line)
            units.append(active_unit)
        if line.startswith("H9"):
            # End of unit
            active_unit = None
        if line.startswith("H4"):
            # Start of session, add to active unit
            active_session = Session(line)
            active_session.unit = active_unit
            active_unit.sessions.append(active_session)
        if line.startswith("H8"):
            # End of session
            active_session.data = np.array(active_data)
            active_data = []
            active_session = None
        if line.startswith("H2"):
            # Station definition, add to active session, or unit if no session active
            if active_session is None:
                active_unit.station = Station(line)
            else:
                active_session.station = Station(line)
        if line.startswith("H3"):
            # Target definition, add to active session, or unit if no session active
            if active_session is None:
                active_unit.target = Target(line)
            else:
                active_session.target = Target(line)
        if line.startswith("10"):
            # Data point, add to active data, which gets added to session at its end
            sline = line.split()
            t = float(sline[1])
            r = float(sline[2])
            active_data.append([t, r])
    return units
        

if __name__=="__main__":
    from sys import argv
    with open(argv[1]) as f:
        U = parse(f.read())
        for u in U:
            for s in u.sessions:
                print(s)
                print(s.target, "\n", s.station)
                print(s.data[:2,:])

