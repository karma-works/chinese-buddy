from __future__ import annotations

import pytest
from langchain_core.messages import AIMessage

from chinese_buddy.tutor import _normalize, extract_text_from_chunk


@pytest.mark.parametrize(
    ("chunk", "expected"),
    [
        ({"model": {"messages": [AIMessage(content="你好！")]}}, "你好！"),
        ({"messages": [AIMessage(content="再见！")]}, "再见！"),
        ("直接文本", "直接文本"),
        ({}, ""),
        (42, ""),
    ],
)
def test_extract_text_from_chunk(chunk, expected):
    assert extract_text_from_chunk(chunk) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("hello", "hello"),
        ("  Hello  ", "hello"),
        ("HELLO WORLD", "hello world"),
        ("  multiple   spaces  ", "multiple spaces"),
        ("", ""),
    ],
)
def test_normalize(value, expected):
    assert _normalize(value) == expected
