Hiptrack
========

A simple Python script to track changes to a file and post them to HipChat.  I
use it for getting alerts when an error log changes.  I'd recommend to
daemonize it with [Supervisor](http://supervisord.org/).

There are no dependencies.

### Usage

    python hiptrack.py [file] [room id] [room token]
