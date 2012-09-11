import hashlib

from tornado import web, gen, ioloop

from operant import point
from operant.storage.tornado_redis import TornadoRedis

# Register the point systems that you want to use in your application
point.register("experience")

# Setup the datastore, we are using tornado-redis with a local redis
# instance.
ds = TornadoRedis({"host": "localhost"})

class User(object):
    """ Fake user class implementation """
    def __init__(self, name):
        self.name = name

    def operant_id(self):
        return int(hashlib.md5(self.name).hexdigest(), 16)

class Index(web.RequestHandler):
    @web.asynchronous
    @gen.engine
    def get(self):
        self.write("<a href='/gimme-points'>Gimme XP!</a>")
        user = User(self.get_argument("user", "anon"))
        pts = point.get("experience")
        res = yield gen.Task(pts.get, ds, user)
        self.write("<p>You currently have {0} XP</p>".format(res))
        self.finish()


class Points(web.RequestHandler):
    @web.asynchronous
    @gen.engine
    def get(self):
        user = User(self.get_argument("user", "anon"))
        pts = point.get("experience")
        res = yield gen.Task(pts.award, ds, user, 10)
        self.write("Yay you now have {0} points".format(res))
        self.finish()

application = web.Application([
    ("/", Index),
    ("/gimme-points", Points),
    ])

if __name__ == "__main__":
    application.listen(8888)
    ioloop.IOLoop.instance().start()
