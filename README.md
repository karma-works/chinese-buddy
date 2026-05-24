# Chinese Buddy

![Chinese Buddy logo](frontend/public/logo.png)

Chinese Buddy is a strict Mandarin tutor for vocabulary, writing practice, and pronunciation support. It teaches five-word groups, generates mnemonics and example sentences, quizzes the learner, validates answers, and stores learner memory locally.

The deployed UI is static and runs on GitHub Pages. The tutor backend runs locally so API keys stay server-side.

## Live UI

GitHub Pages URL:

https://karma-works.github.io/chinese-buddy/

## Tech Stack

- Deep Agents v0.6 for the tutor agent loop.
- LangChain model integrations, starting with OpenAI.
- FastAPI backend.
- SQLite local learner memory.
- React, TypeScript, and Vite frontend.
- Server-Sent Events streaming from backend to UI.
- GitHub Pages for static UI deployment.

## Manual Setup

### 1. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
```

Edit `backend/.env`:

```bash
OPENAI_API_KEY=sk-your-key-here
CHINESE_BUDDY_MODEL=openai:gpt-4.1-mini
CHINESE_BUDDY_DB_PATH=./chinese-buddy.sqlite3
CHINESE_BUDDY_CORS_ORIGINS=http://localhost:5173,http://flywheel1,http://flywheel1:5173,https://flywheel1,https://karma-works.github.io
CHINESE_BUDDY_CORS_ORIGIN_REGEX=^https?://(localhost|127\.0\.0\.1|flywheel1|100\.\d{1,3}\.\d{1,3}\.\d{1,3})(:\d+)?$
```

Start the local backend:

```bash
uvicorn chinese_buddy.main:app --reload --host 0.0.0.0 --port 8000
```

Health check:

```bash
curl http://localhost:8000/health
```

### 2. Frontend for Local Development

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL and keep the backend URL set to:

```text
http://localhost:8000
```

### 3. Hosted GitHub Pages UI

Open:

```text
https://karma-works.github.io/chinese-buddy/
```

Then set the backend URL in the top-right field to:

```text
http://localhost:8000
```

The browser will call your local backend while the UI is served from GitHub Pages.

## MVP Demo Script

1. Start the backend.
2. Open the local or hosted UI.
3. Send: `Teach me 20 Mandarin words for business travel.`
4. Confirm Group 1 streams with five words, pinyin, meanings, examples, and mnemonics.
5. Answer the quiz with at least one intentional mistake.
6. Confirm the tutor corrects you, records the weak word, and retests.
7. Ask a pronunciation or writing follow-up.
8. Restart the backend and confirm memory still exists in `backend/chinese-buddy.sqlite3`.

## Validation

Backend:

```bash
cd backend
source .venv/bin/activate
pytest
ruff check .
```

Frontend:

```bash
cd frontend
npm run build
```

## Project Specs

- [Vision](specs/vision.md)
- [Tech stack recommendation](specs/tech-stack-recommendation.md)
- [Implementation plan](specs/implementation-plan.md)
- [Architecture decisions](specs/adrs)

## License

MIT
