from __future__ import annotations

import pytest

from chinese_buddy.tutor import stream_tutor_response


async def _chat(agent, messages, thread_id):
    parts = []
    async for delta in stream_tutor_response(agent, messages, thread_id=thread_id):
        parts.append(delta)
    return "".join(parts)


@pytest.mark.integration
async def test_lesson_saves_trained_words(agent, store, thread_id):
    await _chat(agent, [{"role": "user", "content": "Teach me 5 business words."}], thread_id)
    assert len(store.load().trained_words) >= 1


