# sleepgraph
A small script to plot a histogram over sleep times, which were manually tracked in an excel-sheet.

Imagine you're having a baby, which sleeps unregularly and want to establish something like a real sleep rhythm. You could just force it on the baby, or you could try to find out whether some kind of pattern is already existing anyway, and build on that. This script helps with that.

It takes sleep data in an excel-sheet (Col1: Day, Col2: Sleep start, Col3: Sleep end), and generates a histogram from the data points.

This was quickly hacked together, works well enough for now, but don't expect miracles.

Required modules:
- matplotlib
- openpyxl
