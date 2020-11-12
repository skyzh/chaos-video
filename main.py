#!/usr/bin/env python
# -*- coding:utf-8 -*-
# functools.partial(func, *args, **keywords) 用于 “冻结” 某些函数的参数或者关键字参数，同时会生成一个带有新标签的对象(即返回一个新的函数)。
# 如果有更多的位置参数提供调用，它们会被附加到 args 中。如果有额外的关键字参数提供，它们将会扩展并覆盖原有的关键字参数。
import functools
import tornado.ioloop
import tornado.web
import tornado.platform.asyncio
from tornado.options import define, options, parse_command_line
from tornado.httpclient import AsyncHTTPClient
import asyncio
from asyncio import sleep
from datetime import datetime

"""
运行服务器(main.py),执行一个批处理文件(.bat || .sh)里面有许多连续执行的命令行命令
这些命令分为三种：测试命令:   /ping	，设置参数命令：/config/get 	/config/set，请求命令 (主):  /proxy/(.*)    /(.*)
用向请求命令chaos server 发送请求时，服务器调用ReverseProxyHandler向代理服务器发送request请求，
得到request 请求结果,write 到web page
Our work:利用chaos server向代理服务器发送request请求时的处理， 模拟真实服务器的延迟和速率限制

Assumption: 这里为了简化我们令测试的请求大小都小于speed，即一个请求在1s内能被传输  
若response文件size大于speed,则需要把response的文件分批write到浏览器
"""

config = {}

i = 0
http_client = AsyncHTTPClient
timeout = 0
time_unit = 1           # 1 second
current_time = 0
tmp_time = 0
size = 0


class ReverseProxyHandler(tornado.web.RequestHandler):
    # define the handle request function
    def handle_request(self, response):
        global i
        self.set_status(response.code)
        for k, v in response.headers.get_all():
            self.add_header(k, v)
        self.write(response.body)
        i -= 1
        if i == 0:
            ioloop.IOLoop.instance().stop()         # 测试结束时侯服务器终止， 真实运行可以删除此行

    async def get(self, url):
        global i, timeout, time_unit, tmp_time, current_time, size
        # wait for latency (ms), sleep unit: seconds
        await sleep(int(config.get("latency", 0)) / 1000)
        # get parameters
        # if not get the upstream settings, then use the default value: options.upsteam
        upstream = config.get("upstream",
                              options.upstream)
        # set the interval to extremely large value so that when we didn't set the speed constrain, the server will
        # never be restricted
        interval = config.get("speed",
                              3000000000)

        """
        当一个新的异步请求到来时， 如果它的delta time > time_unit, 则可以传新的interval 大小的数据 
        size：代表过去累积的量，由于我们loop.call_later的限制，在一个time_unit 内最多减少interval大小
        若 size is still larger than 0, decrease the size by interval for each time_unit
        """
        tmp_time = datetime.now()
        if tmp_time - current_time >= time_unit:
            j = (tmp_time - current_time) / time_unit
            for k in range(0, j):
                if size - interval > 0:
                    size -= interval
                else:
                    size = 0
                    break
            current_time = tmp_time

        # Get the response body size, don't have callbacks
        response = await http_client.fetch(f"http://{upstream}/{url}",
                                           headers=self.request.headers)
        size += len(str(response.body))  # add the size
        i += 1

        # set the constrain
        if size <= interval:
            # size is less than interval, just fetch the request without any timeout
            await http_client.fetch(f"http://{upstream}/{url}", self.handle_request, headers=self.request.headers,
                                    method='GET')
            """             AsyncHTTPClient().fetch() --> 
            1.Executes a request, asynchronously returning an HTTPResponse. The 
            request may be either a string URL or an HTTPRequest object. If it is a string, we construct an 
            HTTPRequest using any additional kwargs: HTTPRequest(request, **kwargs) 
            2.This method returns a .Future 
            whose result is an HTTPResponse. By default, the Future will raise an HTTPError if the request returned a 
            non-200 response code (other errors may also be raised if the server could not be contacted). Instead, 
            if raise_error is set to False, the response will always be returned regardless of the response code. 
            3.If a callback is given, it will be invoked with the HTTPResponse. In the callback interface, 
            HTTPError is not automatically raised. Instead, you must check the response's error attribute or call its 
            ~HTTPResponse.rethrow method.                            
            """
        else:
            if size / interval > 0:
                # we need to delay at least timeout time from now on
                timeout = time_unit * (size / interval)
            loop = ioloop.IOLoop.current()
            loop.call_later(timeout, callback=functools.partial(http_client.fetch, f"http://{upstream}/{url}",
                                                                self.handle_request, self.request.headers,
                                                                'GET'))
            """   loop.call_later()
            Runs the callback after delay seconds have passed.
            Returns an opaque handle that may be passed to remove_timeout to cancel. 
            Note that unlike the asyncio method of the same name, the returned object does not have a cancel() method.
            """


class ConfigGetHandler(tornado.web.RequestHandler):
    def get(self, item):
        self.write(str(config.get(item, "")))  # write the output to the request


class ConfigSetHandler(tornado.web.RequestHandler):
    def get(self, item, value):
        config[item] = value
        self.write("success")


class PingHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world!")


def make_app():
    return tornado.web.Application([
        (r"/(.*)", ReverseProxyHandler),  # The real request, almost all the user use this to request
        (r"/proxy/(.*)", ReverseProxyHandler),  # We implement the speed constraint and latency mechanism here.
        (r"/config/get/(.*)", ConfigGetHandler),  # for check the parameter current settings
        (r"/config/set/(.*)/(.*)", ConfigSetHandler),  # for setting parameters
        (r"/ping", PingHandler),  # for test
    ])


if __name__ == "__main__":
    define('port', default=2334, help='port to listen on')  # set the options.port here
    define('upstream', default='localhost:2333', help='upstream server')  # set the options.upsream here

    parse_command_line()  # Parses global options from the command line.
    # AsyncIOMainLoop creates an .IOLoop that corresponds to the current asyncio event loop (i.e. the one returned by
    # asyncio.get_event_loop()).
    tornado.platform.asyncio.AsyncIOMainLoop().install()
    ioloop = asyncio.get_event_loop()  # get a current asyncio I/O event loop, you can view that as an initialization
    app = make_app()  # Define the application
    # Starts an HTTP server for this application on the given port. This is a convenience alias for creating an
    # .HTTPServer object and calling its listen method.
    app.listen(options.port)
    ioloop.run_forever()  # Run the event loop until stop() is called
