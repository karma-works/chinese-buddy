# ADR 0002: Build a Chat-First Streaming UI

Date: 2026-05-23

## Status

Accepted

## Context

The primary interaction is a tutor conversation. The user asks for vocabulary practice, receives streamed lesson content, answers quizzes, and asks follow-up questions. A dashboard or flashcard-first product would add interface work before validating the core agent behavior.

## Decision

Build the MVP as a local web chat interface with streaming agent responses.

The chat should support:

- Prompting the tutor for a lesson.
- Streaming lesson output.
- Submitting quiz answers.
- Receiving validation and correction.
- Asking follow-up questions during or after a lesson.

## Consequences

- The first UI should optimize conversation flow, readability of Chinese text, and answer entry.
- Dashboards, analytics pages, and standalone flashcard screens are deferred.
- Streaming is part of the acceptance criteria, not a later enhancement.
