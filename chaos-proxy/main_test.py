import pytest
import tornado.web
from main import make_app
from timeit import default_timer as timer

application = make_app()

@pytest.fixture
def app():
    return application

@pytest.mark.gen_test
async def test_config(http_client, base_url):
    response = await http_client.fetch(f"{base_url}/config/set/latency/200")
    assert response.code == 200
    assert response.body == b"success"
    response = await http_client.fetch(f"{base_url}/config/get/latency")
    assert response.code == 200
    assert response.body == b"200"

@pytest.mark.gen_test
async def test_reverse_proxy(http_client, base_url):
    # set upstream
    response = await http_client.fetch(f"{base_url}/config/set/upstream/{base_url[7:]}")
    assert response.code == 200
    assert response.body == b"success"
    response = await http_client.fetch(f"{base_url}/config/get/upstream")
    assert response.body == base_url[7:].encode()
    # set latency
    response = await http_client.fetch(f"{base_url}/config/set/latency/1000")
    # request ping
    start = timer()
    response = await http_client.fetch(f"{base_url}/proxy/ping")
    end = timer()
    assert end - start >= 1.0
    assert response.code == 200
    assert response.body == b"Hello, world!"
