"""
A simple Python script to track changes to a file and post them to HipChat.  I
use it for getting alerts when an error log changes.  I'd recommend to
daemonize it with `Supervisor <http://supervisord.org/>`_.

There are no dependencies.

Usage:  python hiptrack.py [file] [room id] [room token]

"""

import sys
import json
try:
    import httplib
except ImportError:
    import http.client as httplib
import urllib
import subprocess
import threading
from time import sleep
try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty

if len(sys.argv) != 4:
    sys.stderr.write('Incorrect number of arguments.\n')
    sys.stderr.write(
        'Usage:  python hiptrack.py [file] [room id] [room token]\n'
    )
    sys.exit(1)

try:

    q = Queue()

    def reader():
        f = subprocess.Popen(
            ['tail', '-F', sys.argv[1]],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        while True:
            q.put(f.stdout.readline().decode('utf-8'))

    threading.Thread(target=reader).start()

    # We want to ignore the first output
    sleep(1)
    while True:
        try:
            q.get(False)
        except Empty:
            break
    while True:
        message = [q.get()]
        sleep(1)  # Give it a second to write everything
        while True:
            try:
                message.append(q.get(False))
            except Empty:
                break

        url = '/v2/room/{0}/notification'.format(sys.argv[2])
        headers = {
            'Authorization': 'Bearer {0}'.format(sys.argv[3]),
            'content-type': 'application/json',
        }
        body = json.dumps({
            'message': '<br>'.join(message),
            'notify': True,
            'message_form': 'text',
        })
        c = httplib.HTTPSConnection('api.hipchat.com')
        c.request('POST', url, body, headers)
        response = c.getresponse()
        if response.status != 204:
            sys.stderr.write('Error!\n')
            sys.stderr.write(response.read())
            sys.stderr.write('\n\n')
            sys.stderr.write('The following data was not sent:\n')
            sys.stderr.write(message)
            sys.stderr.write('\n\n')

except (KeyboardInterrupt, SystemExit):
    print '\n! Received keyboard interrupt, quitting threads.\n'
    exit()
