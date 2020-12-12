import tornado.ioloop
import tornado.web
import tornado.platform.asyncio
from tornado.options import define, options, parse_command_line
from tornado.httpclient import AsyncHTTPClient
from asyncio import sleep
from datetime import datetime
import time
import random
import platform
import asyncio
import logging

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

config = {}


class Server_Speed_limit:
    def __init__(self, speed, interval):
        self.init_time = datetime.now()
        self.current_time = self.init_time
        self.Length = speed
        self.current_length = self.Length
        self.Interval = interval
        self.Unit_Dispatch_Length = int(self.Length / 100)

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
            if length <= self.Unit_Dispatch_Length:
                self.current_length -= length
                return length
            else:
                self.current_length -= self.Unit_Dispatch_Length
                return self.Unit_Dispatch_Length
        else:
            if self.current_length <= self.Unit_Dispatch_Length:
                tmp = self.current_length
                self.current_length = 0
                return tmp
            else:
                self.current_length -= self.Unit_Dispatch_Length
                return self.Unit_Dispatch_Length

    def get_sleep_time(self):
        delta = self.Interval \
            - (self.precise_time(self.current_time)
               - self.precise_time(self.init_time))
        if delta > 0:
            return delta
        else:
            return 0

    def reset_parameters(self, speed, interval):
        self.Length = speed
        self.Interval = interval


class Advanced_Server_Speed_Limit(Server_Speed_limit):
    """simulate random speed limit ( 1.time random; 2. speed value random)"""

    def __init__(self, interval, min_speed, max_speed):
        super(Advanced_Server_Speed_Limit, self).__init__(min_speed, interval)
        self.min_length = min_speed
        self.max_length = max_speed
        self.interval_count = random.randint(1, 10)

    def refresh(self):
        self.current_time = datetime.now()
        self.interval_count -= 1

    def reserve(self, length):
        self.refresh()
        if (self.precise_time(self.current_time) - self.precise_time(self.init_time)) >= self.Interval:
            self.init_time = self.current_time
            if self.interval_count <= 0:
                self.interval_count = int(random.uniform(1, 10))
                self.Length = random.uniform(self.min_length, self.max_length)
            self.current_length = self.Length

        if length <= self.current_length:
            self.current_length -= length
            return length
        else:
            tmp = self.current_length
            self.current_length = 0
            return tmp

    def reset_parameters(self, interval, min_speed, max_speed):
        self.min_length = min_speed
        self.max_length = max_speed
        self.Length = min_speed
        self.Interval = interval


Advanced_global_limit = Advanced_Server_Speed_Limit(1000, 500, 30000000)
global_limit = Server_Speed_limit(30000000, 1000)


class ReverseProxyHandler(tornado.web.RequestHandler):
    # def initialize(self):
    #     self.Advanced_global_limit = Advanced_Server_Speed_Limit(1000, 500, 30000000)
    #     self.global_limit = Server_Speed_limit(30000000, 1000)

    async def get(self, url):
        logging.info(f"begin transfer {url}")
        mode = config.get("mode", "simple")
        upstream = config.get("upstream",
                              options.upstream)
        interval = int(config.get("interval", 1000))
        if mode == "advanced":
            # advanced mode
            latency_min = int(config.get("latency-min", 0))
            latency_max = int(config.get("latency-max", latency_min + 500))
            latency_rand = random.uniform(latency_min, latency_max)
            speed_min = int(float(config.get("speed-min", 500))
                            * interval / 1000)
            speed_max = int(
                float(config.get("speed-max", speed_min + 30000000)) * interval / 1000)
            jitter_min = int(config.get("jitter-min", 0))
            jitter_max = int(config.get("jitter-max", 100))
            jitter_prob = float(config.get("jitter-prob", 0.05))
            reset_enable = config.get("reset-enable", "false")
            reset_prob = float(config.get("reset-prob", 0.005))

            await sleep(latency_rand)
            try:
                response = await AsyncHTTPClient().fetch(f"http://{upstream}/{url}",
                                                         headers=self.request.headers)
            except tornado.httpclient.HTTPError as e:
                self.set_status(e.response.code)
                return
            body = response.body
            self.set_status(response.code)
            for k, v in response.headers.get_all():
                self.add_header(k, v)
            if not (
                    interval == Advanced_global_limit.Interval and
                    speed_min == Advanced_global_limit.min_length and
                    speed_max == self.Advanced_global_limit.max_length):
                print("Advanced Global limit reset parameters\n")
                # if the parameters have been changed, reset.
                Advanced_global_limit.reset_parameters(
                    interval, speed_min, speed_max)

            while len(body) > 0:
                bytes_to_write = Advanced_global_limit.reserve(len(body))
                self.write(body[:bytes_to_write])
                await self.flush()
                body = body[bytes_to_write:]
                if Advanced_global_limit.current_length == 0:
                    if reset_enable == 'true' and random.random() < reset_prob:
                        # close HTTP connection and break, simulate the network break down）
                        await self.finish()
                        break
                    if random.random() < jitter_prob:
                        # Past average interval/jitter_prob time when cause jitter
                        time.sleep(random.randint(
                            jitter_min, jitter_max) / 1000)

                    Advanced_global_limit.refresh()
                    latency = Advanced_global_limit.get_sleep_time()
                    await sleep(int(latency) / 1000)
        else:
            # simple mode
            logging.info("using simple mode")
            speed = int(float(config.get("speed",
                                         30000000)) * interval / 1000)
            logging.info(f"speed = {speed}")
            await sleep(int(config.get("latency", 0)) / 1000)
            try:
                response = await AsyncHTTPClient().fetch(f"http://{upstream}/{url}",
                                                         headers=self.request.headers)
            except tornado.httpclient.HTTPError as e:
                self.set_status(e.response.code)
                return
            body = response.body
            logging.info("data fetched from upstream")
            self.set_status(response.code)
            for k, v in response.headers.get_all():
                self.add_header(k, v)
            if not (speed == global_limit.Length and interval == global_limit.Interval):
                print('Global limit parameters: Speed: %d , Interval: %d !' % (
                    global_limit.Length, global_limit.Interval))
                global_limit.reset_parameters(speed, interval)
                print("Global limit reset parameters\n")
                print('Global limit parameters: Speed: %d , Interval: %d !' % (
                    global_limit.Length, global_limit.Interval))
                global_limit.reset_parameters(speed, interval)
            while len(body) > 0:
                bytes_to_write = global_limit.reserve(len(body))
                self.write(body[:bytes_to_write])
                try:
                    await self.flush()
                except:
                    break
                body = body[bytes_to_write:]
                if global_limit.current_length == 0:
                    global_limit.refresh()
                    latency = global_limit.get_sleep_time()
                    await sleep(int(latency) / 1000)


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
