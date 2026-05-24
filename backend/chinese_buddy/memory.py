from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


@dataclass(frozen=True)
class LearnerMemory:
    preferences: dict[str, Any]
    trained_words: list[dict[str, Any]]
    weak_words: list[dict[str, Any]]
    topics: list[dict[str, Any]]
    quiz_history: list[dict[str, Any]]


class MemoryStore:
    def __init__(self, db_path: str | None = None) -> None:
        self.db_path = Path(db_path or os.getenv("CHINESE_BUDDY_DB_PATH", "./chinese-buddy.sqlite3"))
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    @contextmanager
    def connect(self):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.executescript(
                """
                create table if not exists preferences (
                    key text primary key,
                    value text not null,
                    updated_at text not null
                );

                create table if not exists trained_words (
                    word text primary key,
                    pinyin text not null default '',
                    meaning text not null default '',
                    hsk_level text not null default '',
                    topic text not null default '',
                    correct_count integer not null default 0,
                    incorrect_count integer not null default 0,
                    last_seen_at text not null
                );

                create table if not exists topics (
                    topic text primary key,
                    trained_count integer not null default 0,
                    last_seen_at text not null
                );

                create table if not exists quiz_attempts (
                    id integer primary key autoincrement,
                    word text not null,
                    prompt text not null,
                    expected_answer text not null,
                    user_answer text not null,
                    correct integer not null,
                    quiz_type text not null,
                    created_at text not null
                );
                """
            )
            self._set_default_preference(connection, "tutor_style", "strict")
            self._set_default_preference(connection, "mnemonic_style", "use the most effective style")
            self._set_default_preference(connection, "preferred_topics", ["business", "social", "travel"])

    def _set_default_preference(self, connection: sqlite3.Connection, key: str, value: Any) -> None:
        exists = connection.execute("select 1 from preferences where key = ?", (key,)).fetchone()
        if exists:
            return
        connection.execute(
            "insert into preferences (key, value, updated_at) values (?, ?, ?)",
            (key, json.dumps(value, ensure_ascii=False), utc_now()),
        )

    def load(self) -> LearnerMemory:
        with self.connect() as connection:
            preferences = {
                row["key"]: json.loads(row["value"])
                for row in connection.execute("select key, value from preferences order by key")
            }
            trained_words = [
                dict(row)
                for row in connection.execute(
                    """
                    select word, pinyin, meaning, hsk_level, topic, correct_count,
                           incorrect_count, last_seen_at
                    from trained_words
                    order by last_seen_at desc
                    limit 80
                    """
                )
            ]
            weak_words = [
                dict(row)
                for row in connection.execute(
                    """
                    select word, pinyin, meaning, hsk_level, topic, correct_count,
                           incorrect_count, last_seen_at
                    from trained_words
                    where incorrect_count > correct_count
                    order by incorrect_count desc, last_seen_at desc
                    limit 30
                    """
                )
            ]
            topics = [
                dict(row)
                for row in connection.execute(
                    "select topic, trained_count, last_seen_at from topics order by last_seen_at desc"
                )
            ]
            quiz_history = [
                dict(row)
                for row in connection.execute(
                    """
                    select word, prompt, expected_answer, user_answer, correct, quiz_type, created_at
                    from quiz_attempts
                    order by created_at desc
                    limit 30
                    """
                )
            ]
        return LearnerMemory(
            preferences=preferences,
            trained_words=trained_words,
            weak_words=weak_words,
            topics=topics,
            quiz_history=quiz_history,
        )

    def summary_for_prompt(self) -> str:
        memory = self.load()
        return json.dumps(
            {
                "preferences": memory.preferences,
                "recent_trained_words": memory.trained_words[:30],
                "weak_words": memory.weak_words,
                "topics": memory.topics,
                "recent_quiz_history": memory.quiz_history[:10],
            },
            ensure_ascii=False,
            indent=2,
        )

    def record_lesson_words(self, words: list[dict[str, Any]], topic: str = "") -> dict[str, Any]:
        now = utc_now()
        with self.connect() as connection:
            for item in words:
                word = str(item.get("word", "")).strip()
                if not word:
                    continue
                connection.execute(
                    """
                    insert into trained_words
                      (word, pinyin, meaning, hsk_level, topic, last_seen_at)
                    values (?, ?, ?, ?, ?, ?)
                    on conflict(word) do update set
                      pinyin = excluded.pinyin,
                      meaning = excluded.meaning,
                      hsk_level = excluded.hsk_level,
                      topic = excluded.topic,
                      last_seen_at = excluded.last_seen_at
                    """,
                    (
                        word,
                        str(item.get("pinyin", "")),
                        str(item.get("meaning", "")),
                        str(item.get("hsk_level", "")),
                        str(item.get("topic", topic)),
                        now,
                    ),
                )
                effective_topic = str(item.get("topic", topic)).strip()
                if effective_topic:
                    connection.execute(
                        """
                        insert into topics (topic, trained_count, last_seen_at)
                        values (?, 1, ?)
                        on conflict(topic) do update set
                          trained_count = trained_count + 1,
                          last_seen_at = excluded.last_seen_at
                        """,
                        (effective_topic, now),
                    )
        return {"saved": len([item for item in words if item.get("word")])}

    def record_quiz_attempt(
        self,
        word: str,
        prompt: str,
        expected_answer: str,
        user_answer: str,
        correct: bool,
        quiz_type: str,
    ) -> dict[str, Any]:
        now = utc_now()
        with self.connect() as connection:
            connection.execute(
                """
                insert into quiz_attempts
                  (word, prompt, expected_answer, user_answer, correct, quiz_type, created_at)
                values (?, ?, ?, ?, ?, ?, ?)
                """,
                (word, prompt, expected_answer, user_answer, int(correct), quiz_type, now),
            )
            counter = "correct_count" if correct else "incorrect_count"
            connection.execute(
                f"""
                insert into trained_words (word, last_seen_at, {counter})
                values (?, ?, 1)
                on conflict(word) do update set
                  {counter} = {counter} + 1,
                  last_seen_at = excluded.last_seen_at
                """,
                (word, now),
            )
        return {"word": word, "correct": correct, "quiz_type": quiz_type}
