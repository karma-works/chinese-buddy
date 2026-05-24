from __future__ import annotations

import json

import pytest

WORD_MEETING = {
    "word": "会议",
    "pinyin": "huìyì",
    "meaning": "meeting",
    "hsk_level": "HSK2",
    "topic": "business",
}


def test_record_lesson_words_persists_word(store):
    store.record_lesson_words([WORD_MEETING])
    memory = store.load()
    assert memory.trained_words[0]["word"] == "会议"
    assert memory.trained_words[0]["pinyin"] == "huìyì"
    assert memory.trained_words[0]["meaning"] == "meeting"


def test_record_lesson_words_persists_topic(store):
    store.record_lesson_words([WORD_MEETING])
    memory = store.load()
    assert memory.topics[0]["topic"] == "business"


def test_record_lesson_words_empty_list(store):
    result = store.record_lesson_words([])
    assert result == {"saved": 0}
    memory = store.load()
    assert memory.trained_words == []


def test_record_lesson_words_skips_blank_word(store):
    store.record_lesson_words([{"word": "", "pinyin": "", "meaning": ""}])
    memory = store.load()
    assert memory.trained_words == []


def test_record_lesson_words_upsert_updates_metadata(store):
    store.record_lesson_words([WORD_MEETING])
    updated = {**WORD_MEETING, "meaning": "conference", "hsk_level": "HSK3"}
    store.record_lesson_words([updated])
    memory = store.load()
    assert len(memory.trained_words) == 1
    assert memory.trained_words[0]["meaning"] == "conference"
    assert memory.trained_words[0]["hsk_level"] == "HSK3"


@pytest.mark.parametrize(
    ("correct", "expected_correct_count", "expected_incorrect_count"),
    [
        (True, 1, 0),
        (False, 0, 1),
    ],
)
def test_record_quiz_attempt_increments_correct_counter(
    store, correct, expected_correct_count, expected_incorrect_count
):
    store.record_lesson_words([WORD_MEETING])
    store.record_quiz_attempt(
        word="会议",
        prompt="Translate meeting into Chinese.",
        expected_answer="会议",
        user_answer="会议",
        correct=correct,
        quiz_type="text_recall",
    )
    memory = store.load()
    assert memory.trained_words[0]["correct_count"] == expected_correct_count
    assert memory.trained_words[0]["incorrect_count"] == expected_incorrect_count


def test_record_quiz_attempt_appears_in_history(store):
    store.record_lesson_words([WORD_MEETING])
    store.record_quiz_attempt(
        word="会议",
        prompt="Translate meeting into Chinese.",
        expected_answer="会议",
        user_answer="会意",
        correct=False,
        quiz_type="text_recall",
    )
    memory = store.load()
    assert memory.quiz_history[0]["user_answer"] == "会意"
    assert memory.quiz_history[0]["word"] == "会议"


def test_multiple_quiz_attempts_accumulate_counts(store):
    store.record_lesson_words([WORD_MEETING])
    for _ in range(3):
        store.record_quiz_attempt(
            word="会议",
            prompt="p",
            expected_answer="会议",
            user_answer="x",
            correct=False,
            quiz_type="text_recall",
        )
    store.record_quiz_attempt(
        word="会议",
        prompt="p",
        expected_answer="会议",
        user_answer="会议",
        correct=True,
        quiz_type="text_recall",
    )
    memory = store.load()
    assert memory.trained_words[0]["incorrect_count"] == 3
    assert memory.trained_words[0]["correct_count"] == 1


def test_weak_words_includes_word_with_more_incorrect_than_correct(store):
    store.record_lesson_words([WORD_MEETING])
    store.record_quiz_attempt(
        word="会议",
        prompt="p",
        expected_answer="会议",
        user_answer="x",
        correct=False,
        quiz_type="text_recall",
    )
    memory = store.load()
    assert memory.weak_words[0]["word"] == "会议"


def test_weak_words_excludes_word_with_more_correct_than_incorrect(store):
    store.record_lesson_words([WORD_MEETING])
    store.record_quiz_attempt(
        word="会议",
        prompt="p",
        expected_answer="会议",
        user_answer="会议",
        correct=True,
        quiz_type="text_recall",
    )
    memory = store.load()
    assert memory.weak_words == []


def test_summary_for_prompt_returns_valid_json(store):
    store.record_lesson_words([WORD_MEETING])
    summary = store.summary_for_prompt()
    data = json.loads(summary)
    assert "preferences" in data
    assert "recent_trained_words" in data
    assert "weak_words" in data
    assert "topics" in data
    assert "recent_quiz_history" in data
