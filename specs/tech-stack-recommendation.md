# Tech Stack Recommendation

Last updated: 2026-05-24

## Recommended Stack

- Agent runtime: Python with `deepagents` v0.6.
- LLM integration: `langchain-openai` pointed at OpenRouter's OpenAI-compatible API.
- Backend: FastAPI.
- Streaming protocol: Server-Sent Events for the MVP.
- Frontend: Vite, React, and TypeScript.
- Styling: plain CSS with a compact design system.
- Local memory: SQLite.
- Data validation: Pydantic.
- Deployment: GitHub Pages for the static UI.
- Local development: run the FastAPI backend locally; point the hosted UI at `http://localhost:8000`.

## Why This Stack

Deep Agents is strongest in Python and sits on top of LangChain and LangGraph. Keeping the agent backend in Python avoids fighting the framework while still letting the UI stay lightweight and easy to deploy.

OpenRouter should be used as the default model gateway. OpenRouter exposes an OpenAI-compatible API at `https://openrouter.ai/api/v1`, so the backend can keep the LangChain OpenAI-compatible client while using `OPENROUTER_API_KEY` and OpenRouter model ids such as `openai/gpt-5.5`.

GitHub Pages can host only static frontend assets. The LLM-backed tutor must run somewhere else because private API keys cannot be safely embedded in a static site. For the MVP, the correct split is:

- Hosted static UI on GitHub Pages.
- Local backend for the Deep Agents tutor and API keys.
- README setup instructions for local backend configuration.

This keeps deployment simple while preserving the real Deep Agents loop required by the product vision.

## Deep Agents Strengths for Chinese Buddy

Deep Agents is a good fit because Chinese Buddy needs more than one-shot generation. The tutor needs to:

- Plan lesson groups.
- Generate vocabulary content.
- Quiz the learner.
- Grade answers.
- Update memory.
- Decide whether to remediate or advance.
- Answer follow-up questions.

Useful Deep Agents capabilities:

- Planning: structure a 20-word request into groups of five and manage progress.
- Tool use: call deterministic memory and grading tools.
- Long-running context: preserve tutor state without stuffing every detail into the prompt.
- Streaming: send visible progress to the chat UI.
- Provider flexibility: swap model providers through LangChain integrations.
- Subagents later: split quality review, mnemonic generation, or quiz grading into specialist roles.

## Recommended Architecture

```text
React GitHub Pages UI
    |
    | Server-Sent Events / JSON
    v
FastAPI local backend
    |
    v
Deep Agents strict tutor
    |
    +-- learner memory tools
    +-- quiz grading tools
    +-- lesson persistence tools
    |
    v
SQLite local memory
```

## Responsibility Split

Use Deep Agents for:

- Conversation orchestration.
- Lesson generation.
- Mnemonic generation.
- Follow-up tutoring.
- Deciding when to use available tools.

Use deterministic backend code for:

- SQLite persistence.
- Quiz attempt records.
- Weak word tracking.
- Topic and word de-duplication.
- Basic progression rules.
- API validation.

This gives the project real agent behavior without making learner state depend entirely on model judgment.
