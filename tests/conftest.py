import pytest
import asyncio

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def asyncio_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()
