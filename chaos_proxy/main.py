import tornado.ioloop
import tornado.web
import tornado.platform.asyncio
from tornado.options import define, options, parse_command_line
from tornado.httpclient import AsyncHTTPClient
import asyncio
from asyncio import sleep
from datetime import datetime
import time

config = {}


class Server_Speed_limit():
    def __init__(self, speed, interval):
        self.init_time = datetime.now()
        self.current_time = self.init_time
        self.Length = int(speed)
        self.current_length = self.Length
        self.Interval = int(interval)

    def refresh(self):
        self.current_time = datetime.now()

    def precise_time(self, now):
        now_timetuple = now.timetuple()
        now_second = time.mktime(now_timetuple)
        now_millisecond = int(now_second * 1000 + now.microsecond / 1000)
        return now_millisecond

    def reserve(self, length):
        self.refresh()

        if (self.precise_time(self.current_time) - self.precise_time(self.init_time)) >= self.Interval:
            self.init_time = self.current_time
            self.current_length = self.Length
        if length <= self.current_length:
            self.current_length -= length
            return length
        else:
            tmp = self.current_length
            self.current_length = 0
            return tmp

    def get_sleep_time(self):
        delta = self.Interval - (self.precise_time(self.current_time) - self.precise_time(self.init_time))
        if delta > 0:
            return delta
        else:
            return 0


class ReverseProxyHandler(tornado.web.RequestHandler):
    async def get(self, url):
        upstream = config.get("upstream",
                              options.upstream)
        speed = config.get("speed",
                           3000000000)
        interval = config.get("interval", 1000)
        await sleep(int(config.get("latency", 0)) / 1000)
        response = await AsyncHTTPClient().fetch(f"http://{upstream}/{url}",
                                                 headers=self.request.headers)
        body = response.body
        global_limit = Server_Speed_limit(speed, interval)  # A
        while len(body) > 0:
            bytes_to_write = global_limit.reserve(len(body))
            self.write(body[:bytes_to_write])
            self.flush()
            body = body[bytes_to_write:]
            global_limit.refresh()
            latency = global_limit.get_sleep_time()
            if len(body) > 0:
                time.sleep(int(latency) / 1000)     # no need to async here


# no need to use async here


class ConfigGetHandler(tornado.web.RequestHandler):
    def get(self, item):
        self.write(str(config.get(item, "")))


class ConfigSetHandler(tornado.web.RequestHandler):
    def get(self, item, value):
        config[item] = value
        self.write("success")


class PingHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world!")


def make_app():
    return tornado.web.Application([
        (r"/proxy/(.*)", ReverseProxyHandler),
        (r"/config/get/(.*)", ConfigGetHandler),
        (r"/config/set/(.*)/(.*)", ConfigSetHandler),
        (r"/ping", PingHandler),
        (r"/(.*)", ReverseProxyHandler),
    ])


if __name__ == "__main__":
    define('port', default=2334, help='port to listen on')
    define('upstream', default='localhost:2333', help='upstream server')

    parse_command_line()
    tornado.platform.asyncio.AsyncIOMainLoop().install()
    ioloop = asyncio.get_event_loop()
    app = make_app()
    app.listen(options.port)

    ioloop.run_forever()
