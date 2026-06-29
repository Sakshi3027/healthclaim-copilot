"use client";
import { useState } from "react";

interface Source {
  claim_id: string;
  payer: string;
  status: string;
  denial_reason: string | null;
  score: number;
}

interface Message {
  role: "user" | "assistant";
  content: string;
  route?: string;
  sources?: Source[];
  latency_ms?: number;
}

const SAMPLE_QUESTIONS = [
  "How many claims were denied by each payer?",
  "Why are UnitedHealthcare claims being denied?",
  "What is the denial rate for Cigna?",
  "Show me denied claims for total knee replacement",
  "Which payer has the highest denial rate?",
];

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState<any>(null);

  const fetchStats = async () => {
    const res = await fetch("http://localhost:8000/stats");
    const data = await res.json();
    setStats(data);
  };

  useState(() => { fetchStats(); });

  const sendMessage = async (question: string) => {
    if (!question.trim() || loading) return;

    const userMsg: Message = { role: "user", content: question };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await res.json();
      const assistantMsg: Message = {
        role: "assistant",
        content: data.answer,
        route: data.route,
        sources: data.sources,
        latency_ms: data.latency_ms,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "❌ Error connecting to API. Make sure the backend is running." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const routeColor: Record<string, string> = {
    sql: "bg-blue-100 text-blue-700",
    rag: "bg-purple-100 text-purple-700",
    both: "bg-green-100 text-green-700",
    blocked: "bg-red-100 text-red-700",
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white border-b px-6 py-4 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">🏥 HealthClaim Copilot</h1>
          <p className="text-sm text-gray-500">Enterprise RAG Agent for Insurance Claim Analysis</p>
        </div>
        {stats && (
          <div className="flex gap-4 text-sm">
            <div className="text-center">
              <div className="font-bold text-gray-900">{stats.total_claims}</div>
              <div className="text-gray-500">Total Claims</div>
            </div>
            <div className="text-center">
              <div className="font-bold text-red-600">{stats.denied_claims}</div>
              <div className="text-gray-500">Denied</div>
            </div>
            <div className="text-center">
              <div className="font-bold text-orange-600">{stats.denial_rate}%</div>
              <div className="text-gray-500">Denial Rate</div>
            </div>
          </div>
        )}
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <aside className="w-64 bg-white border-r p-4 flex flex-col gap-4">
          <div>
            <h2 className="text-xs font-semibold text-gray-500 uppercase mb-2">Sample Questions</h2>
            <div className="flex flex-col gap-2">
              {SAMPLE_QUESTIONS.map((q) => (
                <button
                  key={q}
                  onClick={() => sendMessage(q)}
                  className="text-left text-sm text-gray-700 hover:bg-gray-100 rounded p-2 transition"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>

          {stats && (
            <div>
              <h2 className="text-xs font-semibold text-gray-500 uppercase mb-2">Denials by Payer</h2>
              {Object.entries(stats.denials_by_payer).map(([payer, count]: any) => (
                <div key={payer} className="flex justify-between text-sm py-1">
                  <span className="text-gray-600">{payer}</span>
                  <span className="font-semibold text-red-600">{count}</span>
                </div>
              ))}
            </div>
          )}

          <div>
            <h2 className="text-xs font-semibold text-gray-500 uppercase mb-2">Route Legend</h2>
            <div className="flex flex-col gap-1 text-xs">
              <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded">SQL — structured query</span>
              <span className="bg-purple-100 text-purple-700 px-2 py-1 rounded">RAG — semantic search</span>
              <span className="bg-green-100 text-green-700 px-2 py-1 rounded">BOTH — combined</span>
              <span className="bg-red-100 text-red-700 px-2 py-1 rounded">BLOCKED — guardrail</span>
            </div>
          </div>
        </aside>

        {/* Chat area */}
        <main className="flex-1 flex flex-col">
          <div className="flex-1 overflow-y-auto p-6 flex flex-col gap-4">
            {messages.length === 0 && (
              <div className="flex-1 flex items-center justify-center text-center">
                <div>
                  <div className="text-4xl mb-4">🏥</div>
                  <h2 className="text-xl font-semibold text-gray-700 mb-2">Ask about your claims data</h2>
                  <p className="text-gray-500 text-sm">Try a sample question from the sidebar or type your own.</p>
                </div>
              </div>
            )}

            {messages.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                <div className={`max-w-2xl rounded-lg p-4 ${msg.role === "user" ? "bg-blue-600 text-white" : "bg-white border text-gray-800"}`}>
                  <p className="whitespace-pre-wrap text-sm">{msg.content}</p>

                  {msg.role === "assistant" && (
                    <div className="mt-3 flex flex-col gap-2">
                      <div className="flex items-center gap-2">
                        {msg.route && (
                          <span className={`text-xs px-2 py-0.5 rounded font-medium ${routeColor[msg.route] || "bg-gray-100"}`}>
                            {msg.route.toUpperCase()}
                          </span>
                        )}
                        {msg.latency_ms && (
                          <span className="text-xs text-gray-400">{msg.latency_ms}ms</span>
                        )}
                      </div>

                      {msg.sources && msg.sources.length > 0 && (
                        <div>
                          <p className="text-xs font-semibold text-gray-500 mb-1">Sources</p>
                          <div className="flex flex-wrap gap-1">
                            {msg.sources.map((s) => (
                              <span key={s.claim_id} className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded" title={s.denial_reason || ""}>
                                {s.claim_id} · {s.payer}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex justify-start">
                <div className="bg-white border rounded-lg p-4 text-sm text-gray-500 animate-pulse">
                  Analyzing claims...
                </div>
              </div>
            )}
          </div>

          {/* Input */}
          <div className="border-t bg-white p-4">
            <div className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && sendMessage(input)}
                placeholder="Ask about claims, denials, payers..."
                className="flex-1 border rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                onClick={() => sendMessage(input)}
                disabled={loading || !input.trim()}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
              >
                Ask
              </button>
            </div>
            <p className="text-xs text-gray-400 mt-1">Protected by guardrails · Powered by LangGraph + Groq</p>
          </div>
        </main>
      </div>
    </div>
  );
}
