#!/usr/bin/env python3

from sys import exit

from openpyxl import load_workbook

from optparse import OptionParser
from datetime import datetime, timedelta, time

from matplotlib import pyplot as plt
from matplotlib import dates as mdates

USAGE="""
This script draws a histogram over sleep time from a spreadsheet file."""

class SleepPhase:
    def __init__(self, date=None, starttime=None, endtime=None):
        if not date or not starttime or not endtime:
            raise ValueError("Invalid date/time input!")

        d = str(date.date())

        start = datetime.fromisoformat(d + " " + str(starttime))
        end = datetime.fromisoformat(d + " " + str(endtime))

        if start > end:
            start -= timedelta(days=1)

        self.date = date
        self.starttime = start
        self.endtime = end
    
    def __str__(self):
        d = "%02i:%02i" % (self.duration()/3600, self.duration()%3600/60)
        return "%s: From %s to %s. Duration: %s." % (self.date.date(), self.starttime, self.endtime, d)
    
    def duration(self):
        return (self.endtime - self.starttime).total_seconds()
    
    def in_range(self, point):
        return point.time() > self.starttime.time() and point.time() < self.endtime.time()

class WorkbookReader:
    def __init__(self, filename):
        self._workbook = load_workbook(filename=filename, data_only=True)

    def read_data(self):
        phases = []
        last_date = None

        for cell in self._workbook.active:
            date, start, end = cell[0].value, cell[1].value, cell[2].value
            if date:
                last_date = date
            phases.append(SleepPhase(last_date, start, end))
        
        return phases

def main():
    parser = OptionParser(usage=USAGE)

    parser.add_option("-i", "--infile", dest="infile",
                      help="Input file to read from.")

    options, args = parser.parse_args()

    if not options.infile:
        print("input filename missing.")
        exit(-1)

    infile = options.infile

    if not infile.endswith(".xlsx"):
      infile += ".xlsx"

    reader = WorkbookReader(infile)

    data = reader.read_data()
    
    hist_start = datetime(2000, 1, 1)
    hist_end = hist_start + timedelta(days=1)
    my_time = hist_start
    my_delta = timedelta(seconds=5*60) # 5 minute raster

    hist_data = []

    while my_time < hist_end:
        for d in data:
            if d.in_range(my_time):
                hist_data.append(my_time)

        my_time += my_delta
    
    fig, ax = plt.subplots(1,1)

    ax.hist(hist_data, bins=24, color='lightblue')

    locator = mdates.HourLocator()
    formatter = mdates.AutoDateFormatter(locator)
    formatter.scaled[1/(24)] = '%H:%M'

    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)

    plt.show()

if __name__ == "__main__":
    main()