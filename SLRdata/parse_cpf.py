from datetime import datetime, timedelta
import numpy as np
from scipy.interpolate import BarycentricInterpolator
from jdcal import gcal2jd as date_to_JD
from jdcal import jd2gcal as JD_to_date
from sys import argv

def timestamp_from_datetime(t):
    delta, JD = date_to_JD(t.year, t.month, t.day)
    seconds = t.microsecond / 1e6 + t.second + 60*t.minute + 3600*t.hour
    return int(JD) + seconds / 86400

class Prediction:
    def __init__(self, data):
        self.name = data["name"]
        self.start = data["start"]
        self.end = data["end"]
        self.predictions = sorted(data["predictions"])
        self.Interpolator = None
    def interpolate(self, t):
        if t < self.start or t > self.end:
            raise ValueError("Timestamp ({}) outside range of prediction ({}, {})!".format(t, self.start, self.end))
        t = timestamp_from_datetime(t)
        if self.Interpolator is None or t < self.interp_start or t > self.interp_end:
            self.update_interpolator(t)
        return self.Interpolator(t)
    def update_interpolator(self, t):
        i = 0
        for line in range(1, len(self.predictions)):
            if t < self.predictions[i][0] and t > self.predictions[i-1][0]:
                break
            i += 1
        if i < 5:
            raise ValueError("Cannot interpolate: Timestamp too close to start. Try the previous day's CPF file.")
        if i > len(self.predictions)-5:
            raise ValueError("Cannot interpolate: Timestamp too close to end. Try the next day's CPF file.")
        points = self.predictions[i-5 : i+5]
        X = [p[0] for p in points]
        Y = np.array([p[1] for p in points])
        self.interp_start = X[4]
        self.interp_end = X[5]
        self.Interpolator = BarycentricInterpolator(X, Y)


def parse_CPF(raw_data):
    data = {}
    data["name"] = None
    data["start"] = None
    data["end"] = None
    data["predictions"] = []
    for line in raw_data.split("\n"):
        if line.startswith("H1") or line.startswith("h1"):
            data["name"] = line[35:45]
        elif line.startswith("H2") or line.startswith("h2"):
            data["start"] = datetime(
                year = int(line[26:30]),
                month = int(line[31:33]),
                day = int(line[34:36]),
                hour = int(line[37:39]),
                minute = int(line[40:42]),
                second = int(line[43:45])
            )
            data["end"] = datetime(
                year = int(line[46:50]),
                month = int(line[51:53]),
                day = int(line[54:56]),
                hour = int(line[57:59]),
                minute = int(line[60:62]),
                second = int(line[63:65])
            )
        elif line.startswith("10"):
            sline = [float(x) for x in line.split()]
            t = sline[2] + sline[3] / 86400
            data["predictions"].append((t, sline[5:8]))
    return Prediction(data)

if __name__=="__main__":
    P = Prediction(argv[1])
    for i in range(30):
        print(P.interpolate(P.start + timedelta(seconds=1000+i)))
