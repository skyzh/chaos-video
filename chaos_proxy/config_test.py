import pytest
from main import make_app
from config import set_config, get_config

application = make_app()


@pytest.fixture
def app():
    return application


@pytest.mark.gen_test
async def test_config(http_client, base_url):
    assert await set_config("latency", "200", base_url) == "success"
    assert await get_config("latency", base_url) == "200"
