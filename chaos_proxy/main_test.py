import pytest
from main import make_app, config
from timeit import default_timer as timer
from tornado.options import define
define('upstream', default='localhost:2333', help='upstream server')

application = make_app()


@pytest.fixture
def app():
    return application


@pytest.mark.gen_test
async def test_config(http_client, base_url):
    config["latency"] = 200
    response = await http_client.fetch(f"{base_url}/config/get/latency")
    assert response.code == 200
    assert response.body == b"200"


@pytest.mark.gen_test
async def test_reverse_proxy(http_client, base_url):
    # set upstream
    config["upstream"] = base_url[7:]
    # set latency
    config["latency"] = 1000
    # request ping
    start = timer()
    response = await http_client.fetch(f"{base_url}/proxy/ping")
    end = timer()
    assert end - start >= 1.0
    assert response.code == 200
    assert response.body == b"Hello, world!"
