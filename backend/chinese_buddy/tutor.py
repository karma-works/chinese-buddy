from __future__ import annotations

import json
import os
from collections.abc import AsyncIterator
from difflib import SequenceMatcher
from typing import Any

from deepagents import create_deep_agent
from langchain.tools import tool
from langchain_openai import ChatOpenAI

from .memory import MemoryStore


SYSTEM_PROMPT = """\
You are Chinese Buddy, a strict Mandarin tutor for one learner.

Mission:
- Increase the learner's Mandarin vocabulary and Chinese writing skill.
- Teach vocabulary in groups of five words.
- Include Chinese characters, pinyin, simple English meaning, two natural example sentences
  with English translations, and one memorable pronunciation mnemonic.
- Memory tricks must target pronunciation: pinyin syllable sounds, tone contour, rhythm,
  or an English sound-alike for the spoken word. Do not create mnemonics for the visual
  shape, radicals, or written structure of Chinese characters unless the learner explicitly
  asks for character-writing help.
- Use any pronunciation mnemonic style that improves retention: funny, absurd, visual,
  story-based, culturally grounded, or professional.
- Quiz immediately after each group.
- Validate answers carefully. Do not advance until the learner has corrected the current group.
- Support pronunciation through pinyin and tone-aware explanations.

Rules:
- Audio recognition is out of scope. Do not ask the learner to record audio.
- Generated examples are acceptable, but they must be natural and level-appropriate.
- Prefer business, social, and travel topics unless the learner asks otherwise.
- Label the mnemonic section "Pronunciation Memory Trick" or equivalent, not just
  "Memory Trick", so the learner knows what the trick is for.
- Read learner memory before teaching or grading.
- Save newly taught words with record_lesson_words when you introduce a lesson group.
- Save quiz performance with record_quiz_attempt when you grade answers.
- Avoid repeating words and topics already trained unless they are weak review items.
- Be strict, concise, and helpful.
"""


def _normalize(value: str) -> str:
    return " ".join(value.casefold().strip().split())


def build_chat_model() -> ChatOpenAI:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("Set OPENROUTER_API_KEY in backend/.env before starting the tutor.")

    headers = {
        "HTTP-Referer": os.getenv(
            "OPENROUTER_HTTP_REFERER",
            "https://karma-works.github.io/chinese-buddy/",
        ),
        "X-Title": os.getenv("OPENROUTER_APP_TITLE", "Chinese Buddy"),
    }
    return ChatOpenAI(
        model=os.getenv("CHINESE_BUDDY_MODEL", "openai/gpt-5.5"),
        api_key=api_key,
        base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
        default_headers=headers,
    )


def build_agent(store: MemoryStore):
    @tool
    def load_learner_memory() -> str:
        """Load learner preferences, trained words, weak words, topics, and recent quiz history."""
        return store.summary_for_prompt()

    @tool
    def record_lesson_words(words_json: str, topic: str = "") -> str:
        """Persist lesson words. Input must be JSON array with word, pinyin, meaning, hsk_level, topic."""
        try:
            words = json.loads(words_json)
        except json.JSONDecodeError as exc:
            return json.dumps({"error": f"Invalid JSON: {exc}"})
        if not isinstance(words, list):
            return json.dumps({"error": "Expected a JSON array"})
        return json.dumps(store.record_lesson_words(words, topic), ensure_ascii=False)

    @tool
    def record_quiz_attempt(
        word: str,
        prompt: str,
        expected_answer: str,
        user_answer: str,
        correct: bool,
        quiz_type: str,
    ) -> str:
        """Persist one graded quiz attempt."""
        return json.dumps(
            store.record_quiz_attempt(
                word=word,
                prompt=prompt,
                expected_answer=expected_answer,
                user_answer=user_answer,
                correct=correct,
                quiz_type=quiz_type,
            ),
            ensure_ascii=False,
        )

    @tool
    def grade_short_answer(expected_answer: str, user_answer: str) -> str:
        """Grade a short text answer with simple normalization and similarity."""
        expected = _normalize(expected_answer)
        actual = _normalize(user_answer)
        exact = expected == actual
        ratio = SequenceMatcher(None, expected, actual).ratio()
        return json.dumps(
            {
                "correct": exact or ratio >= 0.86,
                "similarity": round(ratio, 3),
                "expected": expected_answer,
                "user_answer": user_answer,
            },
            ensure_ascii=False,
        )

    model = build_chat_model()
    return create_deep_agent(
        model=model,
        tools=[load_learner_memory, record_lesson_words, record_quiz_attempt, grade_short_answer],
        system_prompt=SYSTEM_PROMPT,
    )


def extract_text_from_chunk(chunk: Any) -> str:
    if isinstance(chunk, str):
        return chunk
    if not isinstance(chunk, dict):
        return ""

    messages = chunk.get("messages")
    if messages is None:
        for value in chunk.values():
            text = extract_text_from_chunk(value)
            if text:
                return text

    if not messages:
        return ""

    message = messages[-1]
    content = getattr(message, "content", None)
    if content is None and isinstance(message, dict):
        content = message.get("content")

    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and item.get("type") == "text":
                parts.append(str(item.get("text", "")))
        return "".join(parts)
    return ""


async def stream_tutor_response(
    agent: Any,
    messages: list[dict[str, str]],
    thread_id: str,
) -> AsyncIterator[str]:
    config = {"configurable": {"thread_id": thread_id}}
    previous = ""
    yielded = False

    async for chunk in agent.astream({"messages": messages}, config=config):
        text = extract_text_from_chunk(chunk)
        if not text:
            continue
        delta = text[len(previous) :] if text.startswith(previous) else text
        previous = text
        if delta:
            yielded = True
            yield delta

    if not yielded and previous:
        yield previous
