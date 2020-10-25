import tornado.ioloop
import tornado.web
import tornado.platform.asyncio
from tornado.options import define, options, parse_command_line
from tornado.httpclient import AsyncHTTPClient
import asyncio
from asyncio import sleep


config = {}


class ReverseProxyHandler(tornado.web.RequestHandler):
    async def get(self, url):
        # wait for latency (ms)
        await sleep(int(config.get("latency", 0)) / 1000)
        upstream = config.get("upstream", options.upstream)
        resp = await AsyncHTTPClient().fetch(f"http://{upstream}/{url}",
                                             headers=self.request.headers)
        self.set_status(resp.code)
        for k, v in resp.headers.get_all():
            self.add_header(k, v)
        self.write(resp.body)


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
