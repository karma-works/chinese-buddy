import React, { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import { Bot, CheckCircle2, Loader2, Send, Settings2, User } from "lucide-react";
import "./styles.css";

type Role = "user" | "assistant";

type Message = {
  role: Role;
  content: string;
};

const defaultApiBase = localStorage.getItem("chineseBuddyApiBase") ?? "http://localhost:8000";

const starterPrompt =
  "Teach me 20 Mandarin words for business travel. Start with Group 1 and quiz me after five words.";

function App() {
  const [apiBase, setApiBase] = useState(defaultApiBase);
  const [draftApiBase, setDraftApiBase] = useState(defaultApiBase);
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "I am ready. Ask for a Mandarin vocabulary lesson. I will teach five words, quiz you, and hold you to full correctness.",
    },
  ]);
  const [input, setInput] = useState(starterPrompt);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState("");
  const bottomRef = useRef<HTMLDivElement | null>(null);
  const threadId = useMemo(() => {
    const existing = sessionStorage.getItem("chineseBuddyThreadId");
    if (existing) return existing;
    const created = crypto.randomUUID();
    sessionStorage.setItem("chineseBuddyThreadId", created);
    return created;
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isStreaming]);

  function saveApiBase() {
    const normalized = draftApiBase.replace(/\/$/, "");
    localStorage.setItem("chineseBuddyApiBase", normalized);
    setApiBase(normalized);
  }

  async function submit(event?: FormEvent) {
    event?.preventDefault();
    const content = input.trim();
    if (!content || isStreaming) return;

    const nextMessages: Message[] = [...messages, { role: "user", content }];
    setMessages([...nextMessages, { role: "assistant", content: "" }]);
    setInput("");
    setError("");
    setIsStreaming(true);

    try {
      const response = await fetch(`${apiBase}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          thread_id: threadId,
          messages: nextMessages.map((message) => ({
            role: message.role,
            content: message.content,
          })),
        }),
      });

      if (!response.ok || !response.body) {
        throw new Error(`Backend returned ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const events = buffer.split("\n\n");
        buffer = events.pop() ?? "";

        for (const rawEvent of events) {
          const line = rawEvent
            .split("\n")
            .find((candidate) => candidate.startsWith("data: "));
          if (!line) continue;
          const payload = JSON.parse(line.slice(6));
          if (payload.error) throw new Error(payload.error);
          if (payload.delta) {
            setMessages((current) => {
              const copy = [...current];
              const last = copy[copy.length - 1];
              copy[copy.length - 1] = { ...last, content: last.content + payload.delta };
              return copy;
            });
          }
        }
      }
    } catch (caught) {
      const message = caught instanceof Error ? caught.message : "Unknown error";
      setError(message);
      setMessages((current) => {
        const copy = [...current];
        const last = copy[copy.length - 1];
        if (last.role === "assistant" && !last.content.trim()) {
          copy[copy.length - 1] = {
            role: "assistant",
            content:
              "I cannot reach the tutor backend yet. Start the local FastAPI server and confirm the backend URL below.",
          };
        }
        return copy;
      });
    } finally {
      setIsStreaming(false);
    }
  }

  return (
    <main className="app-shell">
      <section className="topbar" aria-label="Application header">
        <div className="brand">
          <img src={`${import.meta.env.BASE_URL}logo.png`} alt="" className="brand-mark" />
          <div>
            <h1>Chinese Buddy</h1>
            <p>Strict Mandarin tutor with memory</p>
          </div>
        </div>
        <div className="connection">
          <Settings2 size={18} aria-hidden="true" />
          <input
            aria-label="Backend URL"
            value={draftApiBase}
            onChange={(event) => setDraftApiBase(event.target.value)}
            spellCheck={false}
          />
          <button type="button" onClick={saveApiBase}>
            Save
          </button>
        </div>
      </section>

      <section className="chat-panel" aria-label="Tutor chat">
        <div className="status-row">
          <span>
            <CheckCircle2 size={16} aria-hidden="true" />
            UI deployed as static GitHub Pages
          </span>
          <span>Backend: {apiBase}</span>
        </div>

        <div className="messages">
          {messages.map((message, index) => (
            <article className={`message ${message.role}`} key={`${message.role}-${index}`}>
              <div className="avatar" aria-hidden="true">
                {message.role === "assistant" ? <Bot size={18} /> : <User size={18} />}
              </div>
              <div className="bubble">
                <pre>{message.content}</pre>
              </div>
            </article>
          ))}
          {isStreaming ? (
            <div className="streaming">
              <Loader2 size={16} className="spinner" aria-hidden="true" />
              Tutor is working
            </div>
          ) : null}
          <div ref={bottomRef} />
        </div>

        {error ? <div className="error">Backend error: {error}</div> : null}

        <form className="composer" onSubmit={submit}>
          <textarea
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder="Answer the quiz or ask for a Mandarin lesson..."
            rows={3}
          />
          <button type="submit" disabled={isStreaming || !input.trim()} aria-label="Send message">
            <Send size={20} />
          </button>
        </form>
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
