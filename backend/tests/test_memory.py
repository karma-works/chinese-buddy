from chinese_buddy.memory import MemoryStore


def test_records_lesson_words_and_quiz_attempts(tmp_path):
    store = MemoryStore(str(tmp_path / "memory.sqlite3"))

    store.record_lesson_words(
        [
            {
                "word": "会议",
                "pinyin": "huìyì",
                "meaning": "meeting",
                "hsk_level": "HSK2",
                "topic": "business",
            }
        ]
    )
    store.record_quiz_attempt(
        word="会议",
        prompt="Translate meeting into Chinese.",
        expected_answer="会议",
        user_answer="会意",
        correct=False,
        quiz_type="text_recall",
    )

    memory = store.load()

    assert memory.trained_words[0]["word"] == "会议"
    assert memory.trained_words[0]["incorrect_count"] == 1
    assert memory.weak_words[0]["word"] == "会议"
    assert memory.topics[0]["topic"] == "business"
    assert memory.quiz_history[0]["user_answer"] == "会意"
