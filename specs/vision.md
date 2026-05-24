# Chinese Buddy Vision

Last updated: 2026-05-23

## Purpose

Chinese Buddy is a strict Mandarin learning tutor built for one primary user: the project owner. Its first job is to increase practical Chinese vocabulary and strengthen Chinese writing skills through pronunciation mnemonic lessons, pronunciation support, adaptive quizzes, and persistent learner memory.

The project is also a hands-on vehicle for learning Deep Agents v0.6 and the surrounding LangChain stack. The learning goal must not displace the product goal: the demo should work as a useful local Mandarin tutor, with the agent loop and memory visibly present in the implementation.

## Product Direction

Chinese Buddy teaches Mandarin in short vocabulary groups. Each group contains five words and includes:

- Chinese word and pinyin.
- Simple English meaning.
- Two high-quality generated example sentences with English translations.
- A strong pronunciation mnemonic selected for effectiveness, using any useful style: funny, absurd, visual, story-based, culturally grounded, or professional.
- Immediate quiz after each group.
- Answer validation and correction.
- Follow-up help when the learner asks questions.

The tutor should behave like a strict teacher. It should be direct, accurate, and persistent about mastery. It should not move on just because a lesson was displayed; it should test the learner and use memory to adapt future practice.

## Mnemonic Style

Mnemonics should target pronunciation, not the visual structure of Chinese characters.

The tutor should build memory tricks around:

- Pinyin syllable sounds.
- Tone contour and rhythm.
- English sound-alikes for the spoken word.
- Short scenes that make the pronunciation memorable.

The tutor should not create mnemonics for radicals, stroke shape, or character appearance unless the learner explicitly asks for character-writing help.

## Initial Learning Scope

In scope for the first product version:

- Mandarin vocabulary.
- Chinese writing practice through text recall and Chinese answer entry.
- Pronunciation support through pinyin and pronunciation-oriented prompts.
- Difficulty-aware quiz progression.
- Long-term learner memory.
- Local streaming chat UI.

Out of scope for the first product version:

- Audio recognition.
- Full speech evaluation.
- Formal grammar curriculum.
- Listening comprehension drills.
- Handwriting recognition.
- Wiki documentation workflow.

## Quiz Model

Quizzes should use a mix of formats and should become harder as the learner improves.

Easy checks:

- Multiple choice.
- Chinese-to-English recognition.
- Matching word to meaning.

Harder checks:

- English-to-Chinese recall.
- Pinyin recall.
- Fill-in-the-blank sentence completion.
- Correcting mistakes in Chinese words or pinyin.

The tutor should validate answers, explain mistakes, and continue testing weak items until the learner reaches full correctness for the current group.

## Memory Requirements

Chinese Buddy should remember:

- Words already trained.
- Topics already covered.
- Weak words.
- Difficulty level, especially HSK 1-6.
- Session history.
- User topic preferences.
- Preferred tutoring style and mnemonic style.
- Which mnemonics or quiz types seem effective for the user.

Memory is required for the MVP. It can start local and simple, but it must be real enough for the agent to avoid repeating topics by accident and to adapt practice based on previous performance.

## MVP Definition

The smallest successful demo is a local web chat interface with streaming output where a user can request a Mandarin vocabulary lesson and receive a strict-tutor agent response like:

```text
🧠 Group 1 (Words 1-5)
1. 商务 (shāngwù)

Meaning: business / commercial matters

Examples:
他去北京出差处理商务问题。
(He went to Beijing on a business trip.)
这是一次重要的商务会议。
(This is an important business meeting.)

Pronunciation Memory Trick:
"Shang-woo" -> imagine a woo-ing businessman in Shanghai trying to close deals.

...

🧪 QUIZ 1 (Answer without looking)
A. Translate into English:
商务
会议
预订
客户
护照

B. Translate into Chinese:
meeting
client
passport
to reserve
business
```

The MVP must also:

- Stream the lesson in the UI.
- Accept user quiz answers.
- Validate answers.
- Respond helpfully to follow-up questions.
- Use a Deep Agents based agent loop.
- Persist and use learner memory.
- Demonstrate the selected tech stack rather than mocking the whole agent layer.

## Experience Principles

- Strict mastery: the tutor keeps testing until the current group is correct.
- Useful pronunciation mnemonics over fixed style: choose whatever mnemonic style best helps retention of the spoken word.
- Generated examples are acceptable if they are natural, level-appropriate, and useful.
- Difficulty should adapt over time instead of staying at one quiz format.
- The chat UI should be the main interface, not a dashboard-first product.
- Local-first development is acceptable for the MVP.

## Non-Goals

- Building a broad public language-learning platform.
- Supporting many users.
- Producing a polished mobile app.
- Building a content-authoring CMS.
- Documenting LangChain learnings in `wiki/` as part of the first implementation plan.
