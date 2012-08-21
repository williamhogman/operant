import hashlib

from bottle import route, run, response, request
from gevent.queue import Queue 

from operant import badge
from operant.storage.plain_redis import Redis

# Register the badges you wanna use in your application
# This can be done in a config file
badge.register_badge(badge.BadgePrototype("testbadge1"))

# Setup datastore, we're gonna use redis here...
ds = Redis({"host": "localhost"})

class User(object):
    """ Fake user class implementation """
    def __init__(self, name):
        self.name = name
        
    def operant_id(self):
        return int(hashlib.md5(self.name).hexdigest(), 16)

@route('/gimme-a-badge')
def gimme():
    response.content_type = "text/plain"
    body = Queue()
    body.put("Went to gimme-a-badge...")

    def _result(received):
        if received:
            body.put("Got badge ")
            body.put(received.badge_id)
        body.put(StopIteration)

    # user-id as the md5 of the name just for testing
    user = User(request.query.name or 'anon')
    badge.get_badge("testbadge1").award(ds, user, _result)
    return body

@route("/")
def index():
    return "Go to <a href='/gimme-a-badge'>this page</a>"

run(host="localhost", port=8080, server="gevent")
