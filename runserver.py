import tornado.ioloop
import tornado.web
import tornado.platform.asyncio
from tornado.options import define
import asyncio
import os

from chaos_proxy.main import make_app as make_chaos_app
from blank_server.main import make_app as make_blank_app

define('static_path', default=os.path.join(
    os.path.dirname(__file__), "blank_server/static"), help='static file path')
define('upstream', default='localhost:2333', help='upstream server')


if __name__ == "__main__":
    tornado.platform.asyncio.AsyncIOMainLoop().install()
    ioloop = asyncio.get_event_loop()
    chaos_app = make_chaos_app()
    chaos_app.listen(2334)
    blank_app = make_blank_app()
    blank_app.listen(2333)

    ioloop.run_forever()
