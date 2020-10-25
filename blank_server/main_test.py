import pytest
from main import make_app
from tornado.options import define
import os

define('static_path', default=os.path.join(
    os.path.dirname(__file__), "static"), help='static file path')


application = make_app()


@pytest.fixture
def app():
    return application


@pytest.mark.gen_test
def test_hello_world(http_client, base_url):
    response = yield http_client.fetch(f"{base_url}/ping")
    assert response.code == 200
    assert response.body == b"Hello, world"


@pytest.mark.gen_test
def test_static(http_client, base_url):
    response = yield http_client.fetch(f"{base_url}/static/test.txt")
    assert response.code == 200
    assert response.body == b"Hello, world from static!"


@pytest.mark.gen_test
def test_blank(http_client, base_url):
    response = yield http_client.fetch(f"{base_url}/blank/233")
    assert response.code == 200
    assert len(response.body) == 233
