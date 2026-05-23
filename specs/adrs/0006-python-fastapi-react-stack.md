# ADR 0006: Use Python FastAPI Backend and Static React Frontend

Date: 2026-05-23

## Status

Accepted

## Context

Deep Agents v0.6 is mandatory for the tutor loop. The UI also needs to be deployed on GitHub Pages, which supports static assets but cannot safely host private LLM API keys or a Python runtime.

## Decision

Use a split architecture:

- Python FastAPI backend for the Deep Agents tutor, memory, and API key usage.
- Vite React TypeScript frontend for the chat UI.
- GitHub Pages for hosting the static frontend.
- Local backend setup documented in the README.

## Consequences

- The deployed UI is public and static.
- Users must run the backend locally or deploy it separately to use real tutor responses.
- API keys remain server-side.
- The project can use Deep Agents where it is strongest while still satisfying the GitHub Pages deployment requirement.
