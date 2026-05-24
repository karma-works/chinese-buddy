from __future__ import annotations

import os
import uuid

import pytest
from dotenv import load_dotenv

load_dotenv()

from chinese_buddy.memory import MemoryStore
from chinese_buddy.tutor import build_agent

_TEST_MODEL_DEFAULT = "openai/gpt-4o"


@pytest.fixture
def store(tmp_path):
    return MemoryStore(str(tmp_path / "memory.sqlite3"))


@pytest.fixture
def agent(store, monkeypatch):
    model = os.getenv("CHINESE_BUDDY_TEST_MODEL", _TEST_MODEL_DEFAULT)
    monkeypatch.setenv("CHINESE_BUDDY_MODEL", model)
    return build_agent(store)


@pytest.fixture
def thread_id():
    return str(uuid.uuid4())


def pytest_collection_modifyitems(items):
    if os.getenv("OPENROUTER_API_KEY"):
        return
    skip = pytest.mark.skip(reason="OPENROUTER_API_KEY not set — pass a key to run integration tests")
    for item in items:
        if item.get_closest_marker("integration"):
            item.add_marker(skip)
