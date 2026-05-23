# ADR 0004: Accept Generated Example Sentences for MVP

Date: 2026-05-23

## Status

Accepted

## Context

The original vision asked for real example sentences from movies or books. That introduces sourcing, attribution, copyright, and retrieval complexity before the tutor loop is validated.

## Decision

Use high-quality generated example sentences for the MVP.

Examples should be:

- Natural Mandarin.
- Appropriate for the user's current difficulty.
- Paired with clear English translations.
- Useful for business, social, travel, or user-selected topics.

## Consequences

- The product can move faster without building a content sourcing pipeline.
- The tutor still needs quality controls in the prompt and evaluation flow.
- Real sourced examples can be reconsidered later as an enhancement.
