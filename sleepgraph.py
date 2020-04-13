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
            end += timedelta(days=1)

        self.date = date
        self.starttime = start
        self.endtime = end
    
    def __str__(self):
        d = "%02i:%02i" % (self.duration()/3600, self.duration()%3600/60)
        return "%s: From %s to %s. Duration: %s." % (self.date.date(), self.starttime, self.endtime, d)
    
    def duration(self):
        return (self.endtime - self.starttime).total_seconds()
    
    def in_range(self, point):
        return point.time() >= self.starttime.time() and point.time() <= self.endtime.time()

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

            if not start or not end:
                print(f"Invalid data: {cell}. ignoring line.")
                continue

            phases.append(SleepPhase(last_date, start, end))
        
        return phases

def plot_histogram(data, raster, resolution):
    hist_start = datetime(2000, 1, 1)
    hist_end = hist_start + timedelta(days=1)
    my_time = hist_start
    my_delta = timedelta(seconds=raster*60)

    hist_data = []

    while my_time < hist_end:
        for d in data:
            if d.in_range(my_time):
                hist_data.append(my_time)

        my_time += my_delta
    
    fig, ax = plt.subplots(1,1)

    ax.hist(hist_data, bins=int(24*(60/resolution)), color='lightblue')

    locator = mdates.HourLocator()
    formatter = mdates.AutoDateFormatter(locator)
    formatter.scaled[1/(24)] = '%H:%M'

    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)

    plt.show()

def calculate_average(totals):
    total_sleep = 0
    total_days = 0

    for d in totals.items():
        total_days += 1
        total_sleep +=  d[1]['sum']

    return total_sleep/total_days

def calculate_totals(data, start_day, start_night):
    totals = {}

    for d in data:
        if not totals.get(d.date):
            totals[d.date] = {'sum': 0, 'day': 0, 'night': 0}

        totals[d.date]['sum'] += d.duration()

        key = 'night'
        if  d.starttime.time() >= time(hour=start_day) and d.starttime.time() <= time(hour=start_night):
            key = 'day'
        totals[d.date][key] += d.duration()

    return totals

def main():
    parser = OptionParser(usage=USAGE)

    parser.add_option("-i", "--infile", dest="infile",
                      help="Input file to read from.")
    parser.add_option("-H", "--histogram", dest="histogram", default=False, action="store_true", 
                      help="Plot sleep histogram.")
    parser.add_option("-R", "--raster", dest="raster", default=5,
                      help="Raster in minutes. Default=5")
    parser.add_option("-r", "--resolution", dest="resolution", default=60,
                      help="Resolution in minutes. Default=5")
    parser.add_option("-d", "--start-day", dest="start_day", default=8, type="int",
                      help="start of a day. Default=8")
    parser.add_option("-n", "--start-night", dest="start_night", default=19, type="int",
                      help="start of a night. Default=19h")

    options, args = parser.parse_args()

    if not options.infile:
        print("input filename missing.")
        exit(-1)

    infile = options.infile
    resolution = int(options.resolution)
    raster = int(options.raster)

    if not infile.endswith(".xlsx"):
      infile += ".xlsx"

    reader = WorkbookReader(infile)

    data = reader.read_data()
    totals = calculate_totals(data, options.start_day, options.start_night)
    average = calculate_average(totals)

    for a in totals.items():
        print(str(a[0].date()) + f" : Day: {a[1]['day']/3600.0:04.01f}h,"
                               + f" Night: {a[1]['night']/3600.0:04.01f}h,"
                               + f" Total: {a[1]['sum']/3600.0:04.01f}h")

    print(f"Average sleep time: {average/3600:02.1f}h")

    if options.histogram:
        plot_histogram(data, raster, resolution)

if __name__ == "__main__":
    main()