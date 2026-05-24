# Chinese Buddy Implementation Plan

Last updated: 2026-05-23

## Target MVP

Build a local web chat app that streams responses from a Deep Agents based strict Mandarin tutor. The tutor generates five-word vocabulary groups with pronunciation-focused mnemonics, quizzes the user, validates answers, answers follow-up questions, and persists learner memory.

## Milestone 1: Project Skeleton

Deliverables:

- Create the application structure.
- Add runtime configuration for model provider credentials.
- Add a local development command.
- Add a minimal chat page.
- Add a server endpoint or action for chat messages.

Acceptance criteria:

- The app starts locally.
- The user can open a web page and submit a message.
- The UI can display assistant responses.

## Milestone 2: Streaming Chat

Deliverables:

- Connect the chat UI to a streaming backend response.
- Render partial assistant output as it arrives.
- Preserve conversation turns in the current browser session.
- Handle loading, error, and retry states.

Acceptance criteria:

- A lesson response visibly streams into the page.
- The user can send a follow-up after the streamed response completes.

## Milestone 3: Deep Agents Tutor Loop

Deliverables:

- Implement the strict tutor agent using Deep Agents v0.6.
- Define the tutor system prompt and behavioral policy.
- Support lesson generation for five-word groups.
- Support answer validation and correction.
- Support follow-up explanations.

Acceptance criteria:

- The agent produces the target five-word lesson format.
- Mnemonics target pinyin pronunciation and tones rather than character shapes.
- The agent asks a quiz after each group.
- The agent validates user answers instead of only generating lessons.
- The implementation uses the real Deep Agents agent loop.

## Milestone 4: Learner Memory

Deliverables:

- Define a local learner memory schema.
- Persist trained words, weak words, topics, difficulty, preferences, session history, mnemonic effectiveness, and quiz performance.
- Load relevant memory before each tutor response.
- Update memory after lessons and quizzes.

Acceptance criteria:

- The tutor avoids accidentally repeating already-trained topics or words.
- Incorrect answers are recorded as weak items.
- Later quiz difficulty can use prior performance.
- Memory survives a local app restart.

## Milestone 5: Adaptive Quiz Difficulty

Deliverables:

- Add quiz-type selection based on word difficulty and learner history.
- Use easier checks for new or weak items.
- Move toward recall-based checks after the learner demonstrates recognition.
- Keep testing the current group until all answers are correct.

Acceptance criteria:

- New words can start with recognition or multiple choice.
- Familiar words can be tested with English-to-Chinese, pinyin recall, or fill-in-the-blank prompts.
- The tutor explains mistakes and retests weak answers.

## Milestone 6: MVP Polish and Verification

Deliverables:

- Improve chat readability for Chinese, pinyin, translations, and quizzes.
- Add a seed prompt or quick action for "business/social/travel vocabulary".
- Add basic tests around memory updates and quiz validation if the codebase structure supports it.
- Manually verify the full MVP flow in the browser.

Acceptance criteria:

- A user can complete one full five-word lesson and quiz loop locally.
- Streaming works.
- Memory is updated.
- Follow-up questions are answered in tutor style.
- No wiki documentation is required for MVP completion.

## First Demo Script

1. Start the local app.
2. Open the chat UI.
3. Ask: `Teach me 20 Mandarin words for business travel.`
4. Confirm the tutor streams Group 1 with five words, pinyin, meanings, examples, and pronunciation mnemonics.
5. Submit quiz answers with at least one intentional mistake.
6. Confirm the tutor identifies the mistake, explains the correction, and retests.
7. Ask a follow-up pronunciation or writing question.
8. Restart the app.
9. Confirm memory still reflects trained and weak words.

## Deferred Work

- Audio recognition and speech scoring.
- Dashboard or flashcard-first interface.
- Multi-user accounts.
- Hosted database.
- Real examples from movies or books.
- Formal grammar curriculum.
- Listening comprehension.
- Handwriting recognition.
- Wiki documentation workflow.
