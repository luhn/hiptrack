"""
A simple Python script to test Hiptrack.

Usage:  python writer.py [file]

"""
import sys
from random import uniform
from time import sleep

count = 0
with open(sys.argv[1], 'w') as fh:
    while True:
        sleep(uniform(0.0, 1.0))
        fh.write('{0}\n'.format(count))
        fh.flush()
        count += 1
