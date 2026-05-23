# ADR 0005: Defer Audio Recognition

Date: 2026-05-23

## Status

Accepted

## Context

Pronunciation support matters, but audio recognition would add speech capture, transcription, scoring, permissions, and model integration. The MVP already needs an agent loop, streaming UI, memory, lesson generation, and adaptive quizzes.

## Decision

Include pronunciation support through pinyin and pronunciation-oriented text prompts, but defer audio recognition and speech scoring.

## Consequences

- The MVP can still teach pronunciation basics.
- Quizzes can include pinyin recall and tone-aware text exercises.
- Microphone input, audio recognition, and spoken feedback are future work.
