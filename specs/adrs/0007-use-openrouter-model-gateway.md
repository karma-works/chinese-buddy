# ADR 0007: Use OpenRouter as the Model Gateway

Date: 2026-05-24

## Status

Accepted

## Context

Chinese Buddy needs model flexibility while keeping the backend simple. The previous setup targeted the OpenAI API directly through LangChain. OpenRouter provides an OpenAI-compatible API surface, allowing the project to keep the same LangChain client shape while routing through OpenRouter.

## Decision

Use OpenRouter as the default model gateway.

Backend configuration:

- `OPENROUTER_API_KEY`
- `OPENROUTER_BASE_URL=https://openrouter.ai/api/v1`
- `CHINESE_BUDDY_MODEL=<OpenRouter model id>`
- Optional `OPENROUTER_HTTP_REFERER` and `OPENROUTER_APP_TITLE` headers.

## Consequences

- The backend no longer requires a direct OpenAI API key for normal setup.
- The model can be changed by editing `CHINESE_BUDDY_MODEL`.
- LangChain still uses the OpenAI-compatible chat model integration.
- The README must document OpenRouter key setup instead of direct OpenAI setup.
