# ADR 0003: Start With Local Persistent Learner Memory

Date: 2026-05-23

## Status

Accepted

## Context

Learner memory is central to the product. The tutor needs to remember trained words, weak words, difficulty, topics, session history, preferences, and which mnemonic or quiz styles are effective. The first user is the project owner, so multi-user infrastructure is unnecessary for the MVP.

## Decision

Implement learner memory as local persistent storage for the MVP.

The memory schema should support:

- Trained words.
- Weak words.
- Topic history.
- HSK or difficulty level.
- Session history.
- User preferences.
- Mnemonic effectiveness notes.
- Quiz performance by word.

The exact storage technology can be chosen during implementation, but it should be inspectable and easy to migrate.

## Consequences

- The MVP can stay local-first without introducing accounts or hosted databases.
- The agent must read memory before lesson generation and write memory after quiz evaluation.
- Memory should be designed as a product capability, not as an incidental chat log.
- Future multi-user support will require a migration path, but it is intentionally out of scope now.
