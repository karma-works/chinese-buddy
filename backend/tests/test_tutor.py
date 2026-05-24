from langchain_core.messages import AIMessage

from chinese_buddy.tutor import extract_text_from_chunk


def test_extracts_text_from_nested_deep_agents_model_chunk():
    chunk = {"model": {"messages": [AIMessage(content="你好！")]}}

    assert extract_text_from_chunk(chunk) == "你好！"


def test_extracts_text_from_top_level_message_chunk():
    chunk = {"messages": [AIMessage(content="再见！")]}

    assert extract_text_from_chunk(chunk) == "再见！"
