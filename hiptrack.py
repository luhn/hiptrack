"""
A simple Python script to track changes to a file and post them to HipChat.  I
use it for getting alerts when an error log changes.  I'd recommend to
daemonize it with `Supervisor <http://supervisord.org/>`_.

Tested on Python 2.7 and 3.4, but I believe it should also work on 2.6, 3.2,
and 3.3.  There are no dependencies.

"""

import sys
import json
import argparse
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

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    '--mention',
    help=('The people to mention in each message.  Multiple people can be '
          'defined by separating the names with comments.'),
)
parser.add_argument('file', help='The file to watch.')
parser.add_argument('room_id', help='The room ID to post to.')
parser.add_argument(
    'auth_token',
    help=('The authorization token.  Must have send_notification scope.  The '
          + 'easiest way to acquire this is a room notification token.'),
)
args = parser.parse_args()
if args.mention:
    mentions = args.mention.split(',')
else:
    mentions = list()

q = Queue()

def reader():
    f = subprocess.Popen(
        ['tail', '-F', args.file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    while True:
        q.put(f.stdout.readline().decode('utf-8'))

t = threading.Thread(target=reader)
t.daemon = True  # Thread dies when program is killed.
t.start()

# We want to ignore the first output
sleep(1)
while True:
    try:
        q.get(False)
    except Empty:
        break
while True:
    message = list()
    msg_len = 0
    if mentions:
        mention = '{0}: You may want to look at this.'.format(
            ', '.join('@{0}'.format(m) for m in mentions)
        )
        message.append(mention)
        msg_len += len(mention)
    line = q.get().strip('\n')
    message.append(line)
    msg_len += len(line)
    sleep(1)  # Give it a second to write everything
    while True:
        try:
            line = q.get(False).strip('\n')
            message.append(line)
            msg_len += len(line)
            if msg_len >= 5000:  # Cut off early so we don't hit max msg size
                break
        except Empty:
            break

    url = '/v2/room/{0}/notification'.format(args.room_id)
    headers = {
        'Authorization': 'Bearer {0}'.format(args.auth_token),
        'content-type': 'application/json',
    }
    message  = '\n'.join(message)
    body = json.dumps({
        'message': message,
        'notify': True,
        'message_format': 'text',
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
