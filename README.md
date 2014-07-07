Hiptrack
========

A simple Python script to track changes to a file and post them to HipChat.  I
use it for getting alerts when an error log changes.  I'd recommend to
daemonize it with [Supervisor](http://supervisord.org/).

Tested on Python 2.7 and 3.4, but I believe it should also work on 2.6, 3.2,
and 3.3.  There are no dependencies.

For usage, run `python hiptrack.py -h`
