# Chinese Buddy

![Chinese Buddy logo](frontend/public/logo.png)

Chinese Buddy is a strict Mandarin tutor for vocabulary, writing practice, and pronunciation support. It teaches five-word groups, generates mnemonics and example sentences, quizzes the learner, validates answers, and stores learner memory locally.

The deployed UI is static and runs on GitHub Pages. The tutor backend runs locally so API keys stay server-side.

## Live UI

GitHub Pages URL:

https://karma-works.github.io/chinese-buddy/

## Tech Stack

- Deep Agents v0.6 for the tutor agent loop.
- LangChain OpenAI-compatible model integration pointed at OpenRouter.
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
OPENROUTER_API_KEY=sk-or-your-key-here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_HTTP_REFERER=https://karma-works.github.io/chinese-buddy/
OPENROUTER_APP_TITLE=Chinese Buddy
CHINESE_BUDDY_MODEL=openai/gpt-5.5
CHINESE_BUDDY_DB_PATH=./chinese-buddy.sqlite3
CHINESE_BUDDY_CORS_ORIGINS=http://localhost:5173,http://flywheel1,http://flywheel1:5173,https://flywheel1,https://karma-works.github.io
CHINESE_BUDDY_CORS_ORIGIN_REGEX=^https?://(localhost|127\.0\.0\.1|flywheel1|100\.\d{1,3}\.\d{1,3}\.\d{1,3})(:\d+)?$
```

Create the API key in OpenRouter, then choose any OpenRouter model id that supports tool calling. The default is OpenRouter's GPT-5.5 model id:

```bash
CHINESE_BUDDY_MODEL=openai/gpt-5.5
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

### GitHub Pages and Tailscale HTTPS Caveat

The GitHub Pages UI is served over HTTPS. Browsers block active requests from an HTTPS page to a plain HTTP backend such as:

```text
http://100.86.249.92:8000
```

That browser error usually looks like:

```text
Blocked loading mixed active content
```

Recommended workaround: expose the local backend over HTTPS inside your tailnet with Tailscale Serve.

On the backend machine:

```bash
cd backend
source .venv/bin/activate
uvicorn chinese_buddy.main:app --host 127.0.0.1 --port 8000
```

In another terminal on the same machine:

```bash
tailscale serve --bg https / http://127.0.0.1:8000
tailscale serve status
```

Use the HTTPS tailnet URL shown by `tailscale serve status` as the backend URL in the GitHub Pages UI, for example:

```text
https://flywheel1.<your-tailnet>.ts.net
```

Plain HTTP is still fine when both frontend and backend are opened over HTTP, for example the local Vite UI at `http://100.86.249.92:5173` calling `http://100.86.249.92:8000`.

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
