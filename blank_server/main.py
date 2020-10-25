import tornado.ioloop
import tornado.web
from tornado.options import define, options, parse_command_line
import os


class PingHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")


class BlankHandler(tornado.web.RequestHandler):
    def get(self, size):
        self.write(b" " * int(size))


def make_app():
    return tornado.web.Application([
        (r"/ping", PingHandler),
        (r"/static/(.*)", tornado.web.StaticFileHandler,
         dict(path=options.static_path)),
        (r"/blank/(\d+)", BlankHandler)
    ])


if __name__ == "__main__":
    define('port', default=2333, help='port to listen on')
    define('static_path', default=os.path.join(
        os.path.dirname(__file__), "static"), help='static file path')

    parse_command_line()
    app = make_app()
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()
