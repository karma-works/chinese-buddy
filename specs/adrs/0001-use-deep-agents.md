# ADR 0001: Use Deep Agents for the Tutor Agent

Date: 2026-05-23

## Status

Accepted

## Context

Chinese Buddy is both a usable Mandarin tutor and a learning project for Deep Agents v0.6 and the LangChain stack. The MVP must prove that the agent loop, memory, and streaming behavior are real parts of the product rather than static prompt output.

## Decision

Use Deep Agents v0.6 as the mandatory agent framework for the tutor loop.

Other LangChain stack components may be used where they support the product clearly, especially for model integration, memory, message handling, tools, and streaming. They are not mandatory unless needed.

## Consequences

- The implementation plan must include a real Deep Agents based tutor flow.
- The MVP should expose agent behavior through the chat UI: lesson generation, quiz evaluation, follow-up answers, and memory updates.
- Product design should stay compatible with agent iteration instead of hard-coding a fixed lesson script.
- If Deep Agents adds complexity, the project should still preserve the requirement and reduce scope elsewhere.
