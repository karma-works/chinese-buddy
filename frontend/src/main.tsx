import React, { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import { Bot, CheckCircle2, Info, Loader2, Send, Settings2, User } from "lucide-react";
import "./styles.css";

type Role = "user" | "assistant";

type Message = {
  role: Role;
  content: string;
};

const defaultApiBase = localStorage.getItem("chineseBuddyApiBase") ?? "http://localhost:8000";

const starterPrompt =
  "Teach me 20 Mandarin words for business travel. Start with Group 1 and quiz me after five words.";

function createThreadId() {
  if (globalThis.crypto?.randomUUID) {
    return globalThis.crypto.randomUUID();
  }
  const randomPart = Math.random().toString(36).slice(2);
  return `thread-${Date.now().toString(36)}-${randomPart}`;
}

function formatJsonBlock(raw: string) {
  try {
    return JSON.stringify(JSON.parse(raw), null, 2);
  } catch {
    return "";
  }
}

function findJsonEnd(input: string, start: number) {
  const open = input[start];
  const close = open === "{" ? "}" : "]";
  const stack = [close];
  let inString = false;
  let escaping = false;

  for (let index = start + 1; index < input.length; index += 1) {
    const char = input[index];

    if (inString) {
      if (escaping) {
        escaping = false;
      } else if (char === "\\") {
        escaping = true;
      } else if (char === '"') {
        inString = false;
      }
      continue;
    }

    if (char === '"') {
      inString = true;
    } else if (char === "{" || char === "[") {
      stack.push(char === "{" ? "}" : "]");
    } else if (char === close || char === "}" || char === "]") {
      if (char !== stack.pop()) return -1;
      if (stack.length === 0) return index + 1;
    }
  }

  return -1;
}

function splitMessageContent(content: string) {
  const jsonBlocks: string[] = [];
  let visibleText = "";
  let index = 0;

  while (index < content.length) {
    const char = content[index];
    if (char !== "{" && char !== "[") {
      visibleText += char;
      index += 1;
      continue;
    }

    const end = findJsonEnd(content, index);
    if (end === -1) {
      visibleText += char;
      index += 1;
      continue;
    }

    const candidate = content.slice(index, end);
    const formatted = formatJsonBlock(candidate);
    if (!formatted) {
      visibleText += char;
      index += 1;
      continue;
    }

    jsonBlocks.push(formatted);
    index = end;
  }

  return {
    visibleText: visibleText.replace(/\n{3,}/g, "\n\n").trim(),
    jsonBlocks,
  };
}

function ChatMessage({ message, index }: { message: Message; index: number }) {
  const [showInfo, setShowInfo] = useState(false);
  const { visibleText, jsonBlocks } = useMemo(() => {
    if (message.role === "user") {
      return { visibleText: message.content, jsonBlocks: [] };
    }
    return splitMessageContent(message.content);
  }, [message.content, message.role]);
  const hasInfo = message.role === "assistant" && jsonBlocks.length > 0;
  const displayedText = visibleText || (message.content ? "" : " ");

  return (
    <article className={`message ${message.role}`} key={`${message.role}-${index}`}>
      <div className="avatar" aria-hidden="true">
        {message.role === "assistant" ? <Bot size={18} /> : <User size={18} />}
      </div>
      <div className="bubble">
        <div className="message-body">
          <pre>{displayedText}</pre>
          {hasInfo ? (
            <button
              type="button"
              className="info-button"
              aria-label={showInfo ? "Hide response metadata" : "Show response metadata"}
              title={showInfo ? "Hide response metadata" : "Show response metadata"}
              onClick={() => setShowInfo((current) => !current)}
            >
              <Info size={16} />
            </button>
          ) : null}
        </div>
        {showInfo ? (
          <div className="json-panel">
            {jsonBlocks.map((block, blockIndex) => (
              <pre key={blockIndex}>{block}</pre>
            ))}
          </div>
        ) : null}
      </div>
    </article>
  );
}

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
    const created = createThreadId();
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
            <ChatMessage message={message} index={index} key={`${message.role}-${index}`} />
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
